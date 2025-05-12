import json
import random


class EmailAgeClient:
    def get_email_score(self, email: str) -> str:
        domainname = email.split("@")[1]
        if "fraud" in email:
            return json.dumps(
                {
                    "domainAge": 120,
                    "domainname": domainname,
                    "emailAge": random.randint(0, 30),
                }
            )
        return json.dumps(
            {
                "domainAge": 10200,
                "domainname": domainname,
                "emailAge": random.randint(365, 5_000),
            }
        )


emailage_client = EmailAgeClient()
