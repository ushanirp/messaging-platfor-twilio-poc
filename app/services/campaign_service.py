from app.models.campaign import Campaign
from app.models.template import Template
from app.models.user import User
from app.models.message import Message
from app.services.template_service import TemplateService
from app.services.messaging_service import MessagingService
from app.database.connection import get_db
from flask import current_app

class CampaignService:
    @staticmethod
    def create_campaign(name, topic_id, template_id, segment_id, schedule_type='immediate', 
                       schedule_at=None, rate_limit=None, quiet_start=None, 
                       quiet_end=None, timezone='UTC', created_by=None):
        '''Create a new campaign - simplified to match schema'''
        # Convert to schema-compatible format
        schedule = {
            'type': schedule_type,
            'at': schedule_at
        }
        
        quiet_hours = {}
        if quiet_start and quiet_end:
            quiet_hours = {
                'start': quiet_start,
                'end': quiet_end
            }
        
        campaign = Campaign(
            name = name,
            topic_id=topic_id,
            template_id=template_id,
            schedule=schedule,
            rate_limit=rate_limit or 10,
            quiet_hours=quiet_hours
        )
        return campaign.save()

    @staticmethod
    def launch_campaign(campaign_id):
        '''Launch a campaign'''
        campaign = Campaign.get_by_id(campaign_id)
        if not campaign:
            raise ValueError("Campaign not found")
        
        if campaign.status not in ('DRAFT', 'SCHEDULED'):
            raise ValueError("Campaign not in a launchable state")
        
        template = Template.get_by_id(campaign.template_id)
        
        if not template:
            raise ValueError("Template not found")
        
        # Get all users (or implement segment logic later)
        recipients = User.get_all()
        
        if not recipients:
            raise ValueError("No recipients found")
        
        sent_count = 0
        failed_count = 0
        error_details = []
        
        # Update campaign status to RUNNING
        campaign.status = 'RUNNING'
        campaign.save()
        
        for user in recipients:
            try:
                # Render template with user attributes
                rendered_text = TemplateService.render_template(
                    template.placeholders,
                    user.attributes
                )
            except Exception as e:
                rendered_text = f"[Template rendering error: {e}]"
                error_msg = f"Template error: {e}"
            
            # Send message
            provider_sid = None
            error_msg = None
            
            try:
                provider_sid = MessagingService.send_whatsapp_message(
                    user.phone_number, 
                    rendered_text
                )
                if provider_sid:
                    sent_count += 1
                    print(f"Message sent to {user.phone_number}: {provider_sid}")
                    print(f"Message content: {rendered_text}")
                else:
                    failed_count += 1
                    error_msg = "Twilio returned no message SID"
                    error_details.append(f"{user.phone_number}: No SID returned")
                    print(f"Failed to send to {user.phone_number}: No SID returned")
            except Exception as e:
                failed_count += 1
                error_msg = str(e)
                error_details.append(f"{user.phone_number}: {error_msg}")
                print(f"Failed to send to {user.phone_number}: {error_msg}")
            
            # Create message record
            message = Message(
                campaign_id=campaign.campaign_id,
                phone_number=user.phone_number,
                template_id=template.template_id,
                body=rendered_text,
                provider_message_sid=provider_sid or "failed",
                state='SENT' if provider_sid else 'FAILED',
                error_code=error_msg
            )
            message.save()
        
        # Update campaign status based on results
        if failed_count == len(recipients):
            # All messages failed
            campaign.status = 'FAILED'
            status_message = "All messages failed to send"
        elif failed_count > 0:
            # Some messages failed
            campaign.status = 'PARTIALLY_COMPLETED'
            status_message = f"Sent {sent_count}/{len(recipients)} messages"
        else:
            # All messages sent successfully
            campaign.status = 'COMPLETED'
            status_message = "All messages sent successfully"
        
        campaign.save()
        
        print(f"Campaign {campaign_id} completed: {status_message}")
        
        return {
            "queued": len(recipients),
            "sent": sent_count,
            "failed": failed_count,
            "campaign_status": campaign.status,
            "status_message": status_message,
            "errors": error_details if error_details else None
        }
    
    @staticmethod
    def get_campaign_status(campaign_id):
        '''Get campaign status with message counts'''
        campaign = Campaign.get_by_id(campaign_id)
        if not campaign:
            raise ValueError("Campaign not found")
        
        db = get_db()
        total = db.execute(
            "SELECT COUNT(*) as cnt FROM messages WHERE campaign_id=?", 
            (campaign_id,)
        ).fetchone()['cnt']
        
        counts = {}
        for state in ['QUEUED', 'SENDING', 'SENT', 'DELIVERED', 'FAILED', 'UNDLVD']:
            counts[state] = db.execute(
                "SELECT COUNT(*) as cnt FROM messages WHERE campaign_id=? AND state=?", 
                (campaign_id, state)
            ).fetchone()['cnt']
        
        # Get error details for failed messages
        failed_messages = db.execute(
            "SELECT phone_number, error_code FROM messages WHERE campaign_id=? AND state='FAILED'",
            (campaign_id,)
        ).fetchall()
        
        error_details = []
        for msg in failed_messages:
            if msg['error_code']:
                error_details.append(f"{msg['phone_number']}: {msg['error_code']}")
        
        return {
            "campaign": campaign.to_dict(),
            "total": total,
            "counts": counts,
            "error_details": error_details if error_details else None
        }
    
    @staticmethod
    def get_campaigns_with_stats():
        '''Get all campaigns with message statistics'''
        campaigns = Campaign.get_all()
        result = []
        
        for campaign in campaigns:
            stats = CampaignService.get_campaign_status(campaign.campaign_id)
            campaign_data = campaign.to_dict()
            campaign_data['message_stats'] = {
                'total': stats['total'],
                'sent': stats['counts']['SENT'],
                'failed': stats['counts']['FAILED'],
                'delivered': stats['counts']['DELIVERED']
            }
            result.append(campaign_data)
        
        return result