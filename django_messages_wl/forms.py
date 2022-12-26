from django_messages.forms import ComposeForm
from mainpage.validators import check_utf8mb3


class ExtendedComposeForm(ComposeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields:
            print(f)
        self.fields["body"].validators.append(check_utf8mb3)
