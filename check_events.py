from app import app, db, EventLog

# Create application context
with app.app_context():
    print('Event logs count:', EventLog.query.count())
    print('Sample event logs:', [e.to_dict() for e in EventLog.query.limit(5).all()])