from flask import Blueprint, render_template, current_app
from sqlalchemy.orm import sessionmaker
from app.models import Contact, Interaction
from sqlalchemy import create_engine, desc
from datetime import datetime, timedelta

bp = Blueprint('dashboard', __name__)

# Create engine and session factory
engine = create_engine('sqlite:///round_again.db')
Session = sessionmaker(bind=engine)

@bp.route('/')
def index():
    """Dashboard homepage showing upcoming contacts."""
    session = Session()
    try:
        # Get all contacts to count totals
        all_contacts = session.query(Contact).all()
        
        # Cache the current time for consistent calculations
        now = datetime.utcnow()
        
        # Count overdue contacts - contacts already due
        overdue_contacts = [contact for contact in all_contacts if contact.is_due]
        
        # Count contacts due in the next 7 days - not yet due but will be soon
        due_soon_contacts = [
            contact for contact in all_contacts 
            if not contact.is_due and contact.next_due_date <= now + timedelta(days=7)
        ]
        
        # Get priority contacts (overdue or due in next 7 days)
        priority_contacts = sorted(
            overdue_contacts + due_soon_contacts,
            key=lambda x: x.next_due_date
        )[:5]  # Top 5 priority contacts
        
        # Get recent interactions with contacts included
        recent_interactions = session.query(Interaction)\
            .order_by(desc(Interaction.interaction_date))\
            .limit(5)\
            .all()
        
        # Add current date to context for footer
        context = {
            'title': 'Dashboard',
            'overdue_count': len(overdue_contacts),
            'due_soon_count': len(due_soon_contacts),
            'total_contacts': len(all_contacts),
            'priority_contacts': priority_contacts,
            'recent_interactions': recent_interactions,
            'now': now  # Adding current date for footer
        }
        
        return render_template('dashboard.html', **context)
    finally:
        session.close()
