from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from flask_login import (
    login_required,
    current_user
)

from app.models.group import Group
from app.services.group_service import GroupService
from app.services.receipt_parser_service import ReceiptParserService


receipt_bp = Blueprint("receipt", __name__)

@receipt_bp.route("/scanreceipt/<int:groupid>", methods=["GET", "POST"])
@login_required
def scanreceipt(groupid):

    group = Group.get_group_by_id(groupid)

    if group is None:
        flash("Invalid Group.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":

        image = request.files.get("receipt")

        if image is None or image.filename == "":
            flash("Please upload a receipt image.", "danger")
            return redirect(request.url)

        try:

            image_path = ReceiptParserService.save_image(image)

            receipt = ReceiptParserService.get_data(image_path)

            session["receipt"] = receipt

            return redirect(
                url_for(
                    "receipt.reviewreceipt",
                    groupid=groupid
                )
            )

        except Exception as e:

            flash(
                f"Unable to process receipt. {e}",
                "danger"
            )

            return redirect(request.url)

    return render_template(
        "scanreceipt.html",
        group=group
    )


@receipt_bp.route("/reviewreceipt/<int:groupid>", methods=["GET", "POST"])
@login_required
def reviewreceipt(groupid):
    group = Group.get_group_by_id(groupid)

    if group is None:
        flash("Invalid group.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    if not current_user.id in [gm.user.id for gm in group.members]:
        flash("You are not a member of this group.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    receipt = session.get("receipt")
    print("\nreceipt is", receipt)

    if receipt is None:
        flash("Please upload a receipt first.", "warning")
        return redirect(url_for("receipt.scanreceipt", groupid=groupid))

    members = [gm.user for gm in group.members]

    if request.method == "POST":
            vendor_name = request.form.get('vendor_name', '')
            total_amount = float(request.form.get('total', 0.0))

            member_base_shares = {}   # { member_id: base_item_shares_without_tax }
            items_breakdown = []     
            taxes_breakdown = []     
            discounts_breakdown = [] 

            member_name_map = {member.id: member.name for member in members}

            # -------------------------------------------------------------
            # 1. PROCESS ITEMS AND BASE MEMBER SHARES
            # -------------------------------------------------------------
            item_indices = sorted(list(set(
                key.split('_')[-1] for key in request.form.keys() if key.startswith('item_name_')
            )), key=int)

            total_items_cost = 0.0

            for idx in item_indices:
                item_name = request.form.get(f'item_name_{idx}', f'Item {idx}')
                cost = float(request.form.get(f'item_cost_{idx}', 0.0))
                total_items_cost += cost

                shares_for_this_item = []

                for key, value in request.form.items():
                    if key.startswith(f'share_item_{idx}_member_'):
                        member_id = int(key.split('_')[-1])
                        share_val = float(value or 0.0)
                        if share_val > 0:
                            shares_for_this_item.append((member_id, share_val))
                            # Accumulate base shares (before taxes/discounts)
                            member_base_shares[member_id] = member_base_shares.get(member_id, 0.0) + share_val

                if shares_for_this_item:
                    shares_str = ", ".join([
                        f"{member_name_map.get(m_id, f'Member {m_id}')}: ₹{amt:.2f}" 
                        for m_id, amt in shares_for_this_item
                    ])
                    items_breakdown.append(f"{item_name} (₹{cost:.2f}) -> [Shares: {shares_str}]")
                else:
                    items_breakdown.append(f"{item_name} (₹{cost:.2f}) -> [No active splits]")

            # -------------------------------------------------------------
            # 2. PROCESS TAXES & DISCOUNTS
            # -------------------------------------------------------------
            tax_indices = sorted(list(set(
                key.split('_')[-1] for key in request.form.keys() if key.startswith('tax_name_')
            )), key=int)

            for idx in tax_indices:
                name = request.form.get(f'tax_name_{idx}', '')
                amt = float(request.form.get(f'tax_amount_{idx}', 0.0))
                if name or amt > 0:
                    taxes_breakdown.append(f"{name}: ₹{amt:.2f}")

            discount_indices = sorted(list(set(
                key.split('_')[-1] for key in request.form.keys() if key.startswith('discount_name_')
            )), key=int)

            for idx in discount_indices:
                name = request.form.get(f'discount_name_{idx}', '')
                amt = float(request.form.get(f'discount_amount_{idx}', 0.0))
                if name or amt > 0:
                    discounts_breakdown.append(f"{name}: -₹{amt:.2f}")

            # -------------------------------------------------------------
            # 3. APPLY TAX/DISCOUNT PROPORTIONALITY TO MEMBER SHARES
            # -------------------------------------------------------------
            formatted_member_shares = {}

            if total_items_cost > 0:
                # Multiplier ratio (e.g., if total with tax is ₹638 and items total is ₹605, ratio = 1.0545)
                multiplier = total_amount / total_items_cost
                
                for m_id, base_share in member_base_shares.items():
                    adjusted_share = round(base_share * multiplier, 2)
                    formatted_member_shares[m_id] = adjusted_share
            else:
                formatted_member_shares = {m_id: 0.0 for m_id in member_base_shares}

            # Handle rounding errors (ensure sum of shares equals exact total_amount)
            shares_sum = round(sum(formatted_member_shares.values()), 2)
            diff = round(total_amount - shares_sum, 2)
            if diff != 0 and formatted_member_shares:
                # Adjust the penny difference on the first member's share
                first_member = next(iter(formatted_member_shares))
                formatted_member_shares[first_member] = round(formatted_member_shares[first_member] + diff, 2)

            # -------------------------------------------------------------
            # 4. CONSTRUCT SUMMARY DESCRIPTION STRING
            # -------------------------------------------------------------
            adjusted_shares_desc = [
                f"  • {member_name_map.get(m_id, f'Member {m_id}')}: ₹{amt:.2f}"
                for m_id, amt in formatted_member_shares.items()
            ]

            description_lines = [
                f"--- EXPENSE SUMMARY FOR {vendor_name.upper()} ---",
                f"Vendor: {vendor_name}",
                "",
                "ITEMS & BASE SPLITS:",
                "\n".join(f"  • {item}" for item in items_breakdown) if items_breakdown else "  • None",
                "",
                "TAXES:",
                "\n".join(f"  • {tax}" for tax in taxes_breakdown) if taxes_breakdown else "  • None",
                "",
                "DISCOUNTS:",
                "\n".join(f"  • {disc}" for disc in discounts_breakdown) if discounts_breakdown else "  • None",
                "",
                "FINAL ADJUSTED SHARES (WITH TAXES & DISCOUNTS):",
                "\n".join(adjusted_shares_desc) if adjusted_shares_desc else "  • None",
                "",
                f"TOTAL AMOUNT: ₹{total_amount:.2f}"
            ]

            description_text = "\n".join(description_lines)

            # -------------------------------------------------------------
            # 5. STORE IN SESSION AND REDIRECT
            # -------------------------------------------------------------
            session['expense_draft'] = {
                "vendor_name": vendor_name,
                "total_amount": round(total_amount, 2),
                "member_shares": formatted_member_shares,
                "description": description_text
            }

            return redirect(url_for("expense.addexpense", groupid=groupid))

    return render_template(
        "reviewreceipt.html",
        group=group,
        members=[member.to_dict() for member in members],
        receipt=receipt
    )