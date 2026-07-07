import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.evaluator import Evaluator

def test_eval():
    config = {
        "criteria": {
            "mode": "hybrid",
            "treasure": {
                "mandatory_items": ["laurel"],
                "optional_items": ["laurel", "laurel", "celestial star"],
                "min_optional_count": 2
            },
            "pet": {
                "mandatory_items": [],
                "optional_items": [],
                "min_optional_count": 0
            }
        }
    }
    
    evaluator = Evaluator(config)
    print("Testing Duplicate Evaluator Logic")
    print(f"Target items: {evaluator.all_target_items}")
    print("-" * 30)

    # Scenario 1: Only 1 laurel found (fails because it's consumed by mandatory)
    evaluator.reset()
    evaluator.items_found = {"laurel": 1}
    print("\nScenario 1: Found 1 laurel")
    assert evaluator.final_decision() == False
    
    # Scenario 2: Found 2 laurels (1 mandatory, 1 optional -> not enough optional!)
    evaluator.reset()
    evaluator.items_found = {"laurel": 2}
    print("\nScenario 2: Found 2 laurels")
    assert evaluator.final_decision() == False

    # Scenario 3: Found 3 laurels (1 mandatory, 2 optional -> pass!)
    evaluator.reset()
    evaluator.items_found = {"laurel": 3}
    print("\nScenario 3: Found 3 laurels")
    assert evaluator.final_decision() == True
    
    # Scenario 4: Found 2 laurels and 1 star (1 mandatory laurel, 1 optional laurel, 1 optional star -> pass!)
    evaluator.reset()
    evaluator.items_found = {"laurel": 2, "celestial star": 1}
    print("\nScenario 4: Found 2 laurels and 1 celestial star")
    assert evaluator.final_decision() == True

    print("\nAll duplicate logical assertions passed successfully!")

if __name__ == "__main__":
    test_eval()
