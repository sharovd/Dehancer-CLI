from pydantic import BaseModel, ConfigDict


class LoginWithEmailAndPasswordModel(BaseModel):
    """
    Representation of a login operation result for email/password authentication.

    This model describes the minimal response body returned by the Dehancer Online API when a user attempts
    to authenticate using an email and password combination. It contains only a success indicator.

    Attributes
    ----------
    success : bool
        Whether the server reported the login (authentication) operation as successful.

    """

    model_config = ConfigDict(extra="forbid")

    success: bool
