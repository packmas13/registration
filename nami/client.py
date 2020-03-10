import json
from .session import Session


class MemberNotFound(Exception):
    pass


class Client(object):
    def __init__(self, config, session_cls=Session):
        self.session = session_cls(config)

    def find_member(self, nami_number, grp_number=None):
        search = {"mitgliedsNummber": str(nami_number), "searchType": "MITGLIEDER"}
        if grp_number:
            search["grpNummer"] = str(grp_number)

        data = self.session.get(
            "/ica/rest/nami/search-multi/result-list",
            {"searchedValues": json.JSONEncoder().encode(search), "limit": 1},
        )
        if not data:
            raise MemberNotFound
        return data[0]

    def member_entries(self, member):
        prefix = "entries_"
        for (key, value) in member.items():
            if not key.startswith(prefix):
                continue
            key = key[len(prefix) :]
            yield (key, value)

    def member_normalized(self, member):
        normalization = {
            "vorname": "first_name",
            "nachname": "last_name",
            "email": "email",
            "mitgliedsNummer": "nami",
        }
        genders = {
            "weiblich": "female",
            "männlich": "male",
        }
        data = {}
        for (key, value) in self.member_entries(member):
            if not value:
                continue
            if key in normalization:
                data[normalization[key]] = value
            elif key == "geburtsDatum":
                data["birthday"] = value[:10]
            elif key == "geschlecht" and value in genders:
                data["gender"] = genders[value]

        # Not available on search results:
        # :troop: scout troop to which the participant belongs
        # :age_section: section to which the participant belongs
        # :is_leader: true if participant is a scout leader
        # :diet: special diet requirements like vegetarian
        # :medication: information about diseases and drugs

        # Not revelant from the NaMi:
        # :attendance: dates present on the camp site
        # :comment: additional information
        # :deregistered_at: timestamp of deregistration (if unregistered)
        # :created_at: timestamp of creation of this record
        # :updated_at: timestamp of last update to this record
        return data
