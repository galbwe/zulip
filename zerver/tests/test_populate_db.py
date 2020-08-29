from django.core.management import call_command
from django.utils.timezone import timedelta as timezone_timedelta

from zerver.lib.test_classes import ZulipTestCase
from zerver.models import Message, Reaction
from zilencer.management.commands.populate_db import choose_date_sent


class TestChoosePubDate(ZulipTestCase):
    def test_choose_date_sent_large_tot_messages(self) -> None:
        """
        Test for a bug that was present, where specifying a large amount of messages to generate
        would cause each message to have date_sent set to timezone_now(), instead of the date_sents
        being distributed across the span of several days.
        """
        tot_messages = 1000000
        datetimes_list = [
            choose_date_sent(i, tot_messages, 1) for i in range(1, tot_messages, tot_messages // 100)
        ]

        # Verify there is a meaningful difference between elements.
        for i in range(1, len(datetimes_list)):
            self.assertTrue(datetimes_list[i] - datetimes_list[i-1] > timezone_timedelta(minutes=5))

class PopulateDbTestCase(ZulipTestCase):
    def setUp(self) -> None:
        super().setUp()
        call_command('populate_db')

class TestEmojiAttachments(PopulateDbTestCase):
    def test_emoji_reaction_distribution(self) -> None:
        n_messages_with_reactions = len(set(m.id for m in Reaction.objects.all()))
        n_messages = Message.objects.count()
        percent_messages_with_reaction = n_messages_with_reactions / n_messages
        assert percent_messages_with_reaction > 0.08, f'Expected percent messages with reactions above 0.08. Actual: {percent_messages_with_reaction}'
        assert percent_messages_with_reaction < 0.12, f'Expected percent messages with reactions below 0.12. Actual: {percent_messages_with_reaction}'
