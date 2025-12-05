"""Test script to verify metadata column mapping fix."""

from core.database.database import get_db_session
from core.database.models import ProspectDashboardTemplate, Client
from datetime import datetime
from uuid import uuid4

def test_metadata_mapping():
    """Test that meta_data attribute maps to metadata column."""
    with get_db_session() as session:
        try:
            # Get existing client
            client = session.query(Client).first()
            if not client:
                print("❌ No client found. Creating test client...")
                from uuid import uuid4
                client = Client(
                    id=uuid4(),
                    name="Test Client",
                    industry="Healthcare"
                )
                session.add(client)
                session.commit()
                print(f"✅ Created test client: {client.name}")
            else:
                print(f"✅ Found client: {client.name}")

            # Create a test prospect dashboard template
            template = ProspectDashboardTemplate(
                client_id=client.id,
                name="Test Metadata Mapping",
                description="Testing metadata column fix",
                category="roi-focused",
                target_audience="Health Plan",
                visual_style={
                    "primary_color": "#c62828",
                    "accent_color": "#6a1b9a",
                    "layout": "balanced"
                },
                widgets=[{
                    "widget_id": "w_test",
                    "widget_type": "kpi-card",
                    "title": "Test Widget",
                    "description": "Test",
                    "position": {"row": 1, "col": 1, "row_span": 1, "col_span": 1},
                    "data_requirements": {
                        "query_type": "aggregate",
                        "metrics": [{
                            "name": "test_metric",
                            "expression": "COUNT(*)",
                            "data_type": "number"
                        }]
                    },
                    "analytics_question": "What is the test metric?",
                    "chart_config": {}
                }],
                meta_data={
                    "generated_by": "manual",
                    "llm_model": "test",
                    "generation_timestamp": datetime.utcnow().isoformat(),
                    "key_features": ["Test feature"],
                    "recommended_use_case": "Testing"
                },
                status="draft"
            )

            session.add(template)
            session.commit()

            print(f"✅ Template created with ID: {template.id}")
            print(f"✅ Metadata accessible via meta_data: {template.meta_data is not None}")
            print(f"✅ Metadata content: {template.meta_data.get('recommended_use_case')}")

            # Query it back to verify
            retrieved = session.query(ProspectDashboardTemplate).filter_by(id=template.id).first()
            if retrieved:
                print(f"✅ Template retrieved successfully")
                print(f"✅ Retrieved metadata generated_by: {retrieved.meta_data.get('generated_by')}")

                # Clean up
                session.delete(retrieved)
                session.commit()
                print(f"✅ Test template cleaned up")

            print("\n🎉 SUCCESS: Metadata column mapping is working!")
            print("   ✓ Python attribute 'meta_data' maps to DB column 'metadata'")
            print("   ✓ Can write and read metadata without errors")
            return True

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            session.rollback()
            return False

if __name__ == "__main__":
    success = test_metadata_mapping()
    exit(0 if success else 1)
