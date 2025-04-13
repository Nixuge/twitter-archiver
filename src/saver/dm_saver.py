from objects.dm_conversation import DmConversation
from objects.dm_person import DmPerson
from request.dm_request import DmRequest


# TODO: Save messages too.
class DmSaver:
    grabbed_users: list[DmPerson]
    grabbed_conversations: list[DmConversation]

    def __init__(self):
        self.grabbed_users = []
        self.grabbed_conversations = []
    
    def _perform_iteration(self, start_id: str | None = None):
        print("Performing iteration.")
        req = DmRequest(
            start_id=start_id
        )

        req.do_all()

        self.grabbed_conversations += req.conversations
        self.grabbed_users += req.users
        return req.next_id

    def grab_all_for_action(self):
        # TODO: Handle fails.
        next_id = self._perform_iteration()
        while next_id != None:
            next_id = self._perform_iteration(next_id)

        print(f"Found {len(self.grabbed_conversations)} DM conversations.")



    def just_save_grabbed_no_git(self):
        for conversation in self.grabbed_conversations:
            conversation.save_to_file()

        for user in self.grabbed_users:
            user.save_to_file()
