import yaml
import csv

with open('email_contents.yaml', 'r') as f:
    email_contents = yaml.safe_load(f)

with open('parameters.yaml', 'r') as f:
    context = yaml.safe_load(f)


class DraftEmail:
    def __init__(self, parms_dict):
        self.parms = parms_dict
        self.parms.update(context)
        self.recipient = parms_dict['email']
        self.subject = self.parameterize(email_contents['subject'])
        self.body = self.parameterize(email_contents['body'])

    def parameterize(self, text):
        class Text:
            def __init__(self, text):
                self.val = text

            def fill_text(self, parms):
                for k, v in parms.items():
                    self.val = self.val.replace('{' + k + '}', v)
                return self

        return Text(text).fill_text(self.parms).fill_text(context).val

    def get_contents(self):
        return self.recipient, self.subject, self.body


class DraftEmailIterator:
    def __init__(self):
        self.username = email_contents['sender_email']
        self.password = email_contents['password']
        with open('recipients.csv', 'r') as f:
            self.guests = [DraftEmail(parms) for parms in csv.DictReader(f)]
        self.next_idx = 0

    def next(self):
        if self.next_idx >= len(self.guests):
            return None
        self.next_idx += 1
        return self.guests[self.next_idx - 1]

    def get_credentials(self):
        return self.username, self.password
    