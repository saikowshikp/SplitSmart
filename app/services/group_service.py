from app.models.group import Group
from app.models.group_members import GroupMember


class GroupService:

    @staticmethod
    def create_group(group_name, creator_id):

        if not group_name.strip():
            return False, "Group name cannot be empty."

        group_id = Group.create_group(
            group_name.strip(),
            creator_id
        )

        GroupMember.add_group_member(
            group_id,
            creator_id
        )

        return True, group_id


    @staticmethod
    def join_group(group_id, user):

        group = Group.get_group_by_id(group_id)

        if group is None:
            return False, "Invalid group ID."

        if GroupMember.is_member(group_id, user.id):
            return False, "You are already a member of this group."

        GroupMember.add_group_member(
            group_id,
            user.id
        )

        return True, group