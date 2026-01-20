from dataclasses import dataclass


@dataclass(frozen=True)
class SilverEarningConfiguration:
    silverPerChatMessage: int
    silverPerPollVote: int
    chatRewardCooldownSeconds: float
