from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.models import Contact, Interaction, InteractionType
from sqlalchemy import create_engine

bp = Blueprint('interactions', __name__, url_prefix='/interactions')

# Create engine and session factory
engine = create_engine('sqlite:///round_again.db')
Session = sessionmaker(bind=engine)

@bp.route('/add/<int:contact_id>', methods=['GET', 'POST'])
def add_interaction(contact_id):
    """Add a new interaction for a contact."""
    session = Session()
    try:
        # Current time for consistency
        now = datetime.utcnow()
        
        if request.method == 'POST':
            interaction_date_str = datetime.strptime(request.form.get('interaction_date'), '%Y-%m-%dT%H:%M')
            
            # Process form submission
            interaction = Interaction(
                contact_id=contact_id,
                interaction_type=InteractionType(request.form.get('interaction_type')),
                interaction_date=interaction_date_str,
                notes=request.form.get('notes')
            )
            
            session.add(interaction)
            session.commit()
            
            flash('Interaction logged successfully!', 'success')
            return redirect(url_for('contacts.detail', contact_id=contact_id))
        
        # Get contact for form
        contact = session.query(Contact).get(contact_id)
        if not contact:
            flash('Contact not found!', 'danger')
            return redirect(url_for('contacts.list_contacts'))
            
        return render_template('interaction_form.html', 
                               title='Add Interaction',
                               contact=contact,
                               interaction_types=InteractionType.__members__.values(),
                               now=now
        )
    except Exception as e:
        session.rollback()
        flash(f'Error logging interaction: {str(e)}', 'danger')
        return redirect(url_for('contacts.detail', contact_id=contact_id))
    finally:
        session.close()

@bp.route('/new/<int:contact_id>', methods=['GET'])
def new_form(contact_id):
    """Show form to add a new interaction."""
    session = Session()
    try:
        # Current time for consistency
        now = datetime.utcnow()
        
        contact = session.query(Contact).get(contact_id)
        if not contact:
            flash('Contact not found!', 'danger')
            return redirect(url_for('contacts.list_contacts'))
            
        return render_template('interaction_form.html', 
                               title='Log Interaction',
                               contact=contact,
                               interaction_types=InteractionType.__members__.values(),
                               now=now
        )
    finally:
        session.close()