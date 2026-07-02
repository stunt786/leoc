from app import app, db, EventLog
from datetime import datetime, timedelta, date

def test_event_log_filtering():
    with app.app_context():
        # Clean up existing logs for testing
        EventLog.query.delete()
        db.session.commit()

        # Create events
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Event 1: Today
        e1 = EventLog(
            timestamp=datetime.now(),
            event_type="Test Today",
            description="Event happened today",
            location="Loc1"
        )
        
        # Event 2: Yesterday
        e2 = EventLog(
            timestamp=datetime.now() - timedelta(days=1),
            event_type="Test Yesterday",
            description="Event happened yesterday",
            location="Loc2"
        )
        
        db.session.add_all([e1, e2])
        db.session.commit()
        
        print(f"Created events: Today ({today}), Yesterday ({yesterday})")
        
        # Test Query using func.date (Start Date = Today, End Date = Today)
        start_date = today
        end_date = today
        
        print(f"\nFiltering for: {start_date} to {end_date}")
        
        logs = EventLog.query.filter(
            db.func.date(EventLog.timestamp) >= start_date,
            db.func.date(EventLog.timestamp) <= end_date
        ).all()
        
        print(f"Found {len(logs)} logs:")
        for log in logs:
            print(f"- {log.timestamp}: {log.event_type}")
            
        if len(logs) == 1 and logs[0].event_type == "Test Today":
            print("\nSUCCESS: Filtering worked correctly.")
        else:
            print("\nFAILURE: Filtering returned unexpected results.")

if __name__ == "__main__":
    test_event_log_filtering()
