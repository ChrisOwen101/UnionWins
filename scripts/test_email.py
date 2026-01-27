"""
Test script to send a test email using Resend.
"""
import sys
from pathlib import Path

# Add the backend/src directory to the path
backend_path = Path(__file__).parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_path))

import resend
from config import RESEND_API_KEY, FROM_EMAIL

# Initialize Resend
resend.api_key = RESEND_API_KEY

def send_test_email(to_email: str, use_test_domain: bool = True):
    """Send a test email using Resend."""
    
    # Use Resend's test domain if not verified
    from_email = "onboarding@resend.dev" if use_test_domain else FROM_EMAIL
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Test Email from Union Wins</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; margin: 0; padding: 0; background-color: #ffffff;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <!-- Header -->
            <div style="text-align: center; padding: 24px 0; border-bottom: 2px solid #ef4444;">
                <h1 style="margin: 0; font-size: 24px; color: #111827;">
                    ✊ What Have Unions Done For Us?
                </h1>
                <p style="margin: 8px 0 0 0; font-size: 14px; color: #6b7280;">
                    Test Email
                </p>
            </div>
            
            <!-- Body -->
            <div style="padding: 32px 0;">
                <h2 style="font-size: 20px; color: #111827; margin: 0 0 16px 0;">
                    Test Email Successful! 🎉
                </h2>
                
                <p style="font-size: 14px; color: #374151; margin: 0 0 16px 0; line-height: 1.6;">
                    This is a test email from the Union Wins platform. If you're seeing this, 
                    it means the Resend email service is configured correctly and working!
                </p>
                
                <div style="margin: 24px 0; padding: 16px; background-color: #f9fafb; border-left: 4px solid #ef4444; border-radius: 4px;">
                    <h3 style="margin: 0 0 8px 0; font-size: 16px; color: #111827;">
                        ✅ Email Service Status
                    </h3>
                    <p style="margin: 0; font-size: 14px; color: #374151;">
                        Your Resend integration is working properly. You can now send newsletter emails to subscribers.
                    </p>
                </div>
                
                <p style="font-size: 14px; color: #374151; margin: 24px 0 0 0; line-height: 1.6;">
                    Next steps:
                </p>
                <ul style="font-size: 14px; color: #374151; line-height: 1.8;">
                    <li>Verify the email arrived in your inbox</li>
                    <li>Check the formatting looks correct</li>
                    <li>Test with different email providers if needed</li>
                </ul>
            </div>
            
            <!-- Footer -->
            <div style="border-top: 1px solid #e5e7eb; padding: 24px 0; text-align: center;">
                <p style="font-size: 12px; color: #6b7280; margin: 0;">
                    <a href="https://whathaveunionsdoneforus.uk/" style="color: #ef4444; text-decoration: none;">Visit Website</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        print(f"Sending test email to: {to_email}")
        print(f"From: {from_email}")
        if use_test_domain:
            print("📧 Using Resend test domain (onboarding@resend.dev)")
        
        params = {
            "from": from_email,
            "to": [to_email],
            "subject": "✊ Test Email from Union Wins",
            "html": html_content,
        }
        
        response = resend.Emails.send(params)
        
        print(f"\n✅ Email sent successfully!")
        print(f"Email ID: {response['id']}")
        return response
        
    except Exception as e:
        print(f"\n❌ Error sending email: {str(e)}")
        raise


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_email.py <email_address>")
        print("Example: python test_email.py your.email@example.com")
        sys.exit(1)
    
    to_email = sys.argv[1]
    send_test_email(to_email, False)
