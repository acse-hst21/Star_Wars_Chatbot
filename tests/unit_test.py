import pytest
from src.app import select_weighted_prompt, Prompt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.app import Base
from src.config import DEFAULT_PROMPTS

# Create a test database
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
SessionTesting = sessionmaker(bind=engine)

@pytest.fixture(scope="function")
def session():
    """Creates a new database session for each test."""
    Base.metadata.create_all(engine)  # Create tables
    session = SessionTesting()
    yield session
    session.close()
    Base.metadata.drop_all(engine)  # Drop tables after test

def test_select_weighted_prompt_with_data(session):
    """Tests that a weighted prompt is selected correctly."""
    session.add_all([
        Prompt(prompt="Hello, world!", name='Hello world', weight=1.0),
        Prompt(prompt="How can I help?", name='Friendly message', weight=2.0)
    ])
    session.commit()
    
    prompt, prompt_version, weight = select_weighted_prompt(session)
    assert prompt in ["Hello, world!", "How can I help?"], "Prompt should be selected from available prompts."
    assert float(weight) in [1.0, 2.0], "Weight should match one of the defined weights."

def test_select_weighted_prompt_no_data(session):
    """Tests that the function returns a default prompt when no prompts exist."""
    prompt, prompt_version, weight = select_weighted_prompt(session)
    
    assert prompt == DEFAULT_PROMPTS[0]["prompt"], "Default prompt should be returned."
    assert float(weight) == DEFAULT_PROMPTS[0]["weight"], "Default weight should be returned."

def test_select_weighted_prompt_weight_distribution(session):
    """Tests that prompts with higher weights are selected more often."""
    session.add_all([
        Prompt(prompt="Low weight", name='low', weight=1.0),
        Prompt(prompt="High weight", name='high', weight=10.0)
    ])
    session.commit()
    
    high_weight_count = 0
    low_weight_count = 0
    
    for _ in range(1000):
        prompt, _, _ = select_weighted_prompt(session)
        if prompt == "High weight":
            high_weight_count += 1
        else:
            low_weight_count += 1
    
    assert high_weight_count > low_weight_count, "Higher-weighted prompts should be selected more often."
