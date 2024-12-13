from bson import ObjectId
import requests
import secrets
from datetime import datetime

from app.config import settings

def send_verification_email(email: str, token: str):
    verify_url = f"{settings.FRONTEND_URL}/verify-email/{token}"
    
    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{settings.MAILGUN_DOMAIN}/messages",
            auth=("api", settings.MAILGUN_API_KEY),
            data={
                "from": f"Grail <mailgun@{settings.MAILGUN_DOMAIN}>",  # Updated sender format
                "to": email,  # Single email as string instead of list
                "subject": "Verify your email",
                "html": f"""
                    <table style="width: 100%; height: 600px; background-color: #2b4099; font-family: Arial, sans-serif; font-size: 16px; border-collapse: collapse;">
  <tr>
    <td align="center" valign="middle">
      <!-- Inner container (the card) -->
      <table style="width: 50%; background-color: white; border: 4px solid #89CAFF; padding: 20px; border-radius: 10px;">
        <tr style="margin-top: 16px">
          <td style="text-align: center;">
            <img src="https://thegrail.app/big_logo.png" width="50%" height="auto" style="margin-bottom: 16px;" />
          </td>
        </tr>
        <tr style="margin-bottom: 16px">
          <td style="font-size: 20px; font-weight: bold; text-align: center; margin-bottom: 16px;">👋🏼 Hi there,</td>
        </tr>
        <tr style="margin-bottom: 16px">
          <td style="text-align: center; margin-bottom: 16px;">You&rsquo;re receiving this message because you recently signed up for an account.</td>
        </tr>
        <tr style="margin-bottom: 16px">
          <td style="text-align: center; margin-bottom: 16px;">Please verify that your email address is {email}, and that you entered it when signing up for The Grail.</td>
        </tr>
        <tr style="margin-bottom: 16px">
          <td style="text-align: center; margin-bottom: 16px;">
            <a href={verify_url} style="display: inline-block; border-radius: 10px; background-color: #2b4099; color: white; box-shadow: 0 4px 4px rgba(0, 0, 0, 0.3); padding: 4px 64px; text-decoration: none;">Verify email</a>
          </td>
        </tr>
        <tr style="margin-bottom: 16px">
          <td style="text-align: center;">If you didn’t request this email, there’s nothing to worry about. You can safely ignore it!</td>
        </tr>
      </table>
    </td>
  </tr>
</table>
                """
            }
        )
        
        if not response.ok:
            print(f"Failed to send email. Status code: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
        return True
        
    except Exception as e:
        print(f"Exception while sending email: {str(e)}")
        return False
    
def create_verification_token() -> str:
    return secrets.token_urlsafe(32)

async def verify_email_token(token: str):
    from app.crud.user import get_user_by_verification_token, update_user_verified_status  # Local import to avoid circular import
    user = await get_user_by_verification_token(token)
    if not user:
        return None
    
    if user.email_verification_expires < datetime.now():
        return None
    
    await update_user_verified_status(user.id, True)
    return user