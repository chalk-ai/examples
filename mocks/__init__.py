import random

from dataclasses import dataclass


@dataclass
class UserIdentity:
    name: str
    email: str


class UserService:
    domains = ["gmail.com", "chalk.ai", "nasa.gov"]
    names = ["Monica", "Justine", "Sam", "Nikhil"]

    def get_identity(self, id: int) -> UserIdentity:
        random.seed(id)
        name = random.choice(self.names)
        return UserIdentity(
            name=name,
            email=f"{name.lower()}@{random.choice(self.domains)}",
        )


user_service = UserService()


@dataclass
class EmailRisk:
    age_years: float
    risk_score: float


class LexusNexus:
    def get_email_risk(self, email: str) -> EmailRisk:
        random.seed(email)
        return EmailRisk(
            age_years=random.uniform(0, 10),
            risk_score=random.uniform(0, 1),
        )


lexus_nexus = LexusNexus()
