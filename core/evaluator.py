import os
from collections import defaultdict
from .logger import logger
from .detector import Detector
from .ocr import WindowsOCR

class Evaluator:
    def __init__(self, config):
        self.config = config
        self.detector = Detector(config=config, template_dir="templates/desired")
        self.ocr = WindowsOCR()
        self.criteria = config.get("criteria", {})
        
        self.eval_mode = self.criteria.get("mode", "hybrid").lower()
            
        # Treasure criteria
        treasure = self.criteria.get("treasure") or {}
        self.treasure_mandatory = treasure.get("mandatory_items") or []
        self.treasure_optional = treasure.get("optional_items") or []
        self.treasure_min_opt = treasure.get("min_optional_count") or 0
        
        # Pet criteria
        pet = self.criteria.get("pet") or {}
        self.pet_mandatory = pet.get("mandatory_items") or []
        self.pet_optional = pet.get("optional_items") or []
        self.pet_min_opt = pet.get("min_optional_count") or 0
        
        # Flatten all into a single list for scanning
        self.all_target_items = list(set(
            self.treasure_mandatory + self.treasure_optional + 
            self.pet_mandatory + self.pet_optional
        ))
        
        self.items_found = defaultdict(int)
        self.all_drawn_items = []

    def reset(self):
        """Reset found items for a new session."""
        self.items_found = defaultdict(int)
        self.all_drawn_items = []
        
    def evaluate_screen(self, screen_img, draw_type=None):
        """Check the current screen image for any target items."""
        found_in_this_screen = []
        
        ocr_text = ""
        if self.eval_mode in ["text", "hybrid"]:
            ocr_text = self.ocr.recognize(screen_img)
            if ocr_text:
                clean_text = ocr_text.replace('\n', ' | ').strip()
                logger.info(f"Screen text read by OCR: {clean_text}")
                
                # Dynamic parsing
                if draw_type:
                    import re
                    parsed_name = None
                    clean_lower = clean_text.lower()
                    
                    if "treasure" in draw_type.lower():
                        # Look for text between "treasure received!" and "*" or "•"
                        match = re.search(r"treasure received!\s*(.*?)\s*[\*•]", clean_lower)
                        if match:
                            parsed_name = match.group(1).strip()
                    elif "pet" in draw_type.lower():
                        # Look for text between the first "!" (after congratulations) and "hatched" or "!"
                        # e.g. "congratulations! snow globe hatched!" -> "snow globe"
                        # We use a non-greedy match to grab exactly the pet name.
                        match = re.search(r"!\s*(.*?)\s*(?:hatched|!)", clean_lower)
                        if match:
                            parsed_name = match.group(1).strip()
                            
                    if parsed_name:
                        tag = "TREASURE" if "treasure" in draw_type.lower() else "PET"
                        if tag == "TREASURE":
                            logger.treasure(parsed_name.title())
                        else:
                            logger.pet(parsed_name.title())
                        self.all_drawn_items.append((tag, parsed_name.title()))
                
        for item in self.all_target_items:
            found = False
            # Check Text
            if self.eval_mode in ["text", "hybrid"] and ocr_text:
                if item.lower() in ocr_text:
                    logger.rainbow(f"Desired item matched via OCR text: '{item}'")
                    found = True
                    
            # Check Image
            if not found and self.eval_mode in ["image", "hybrid"]:
                template_path = item
                if not template_path.endswith(".png"):
                    template_path += ".png"
                    
                result = self.detector.find(template_path, screen_img=screen_img)
                if result:
                    logger.rainbow(f"Desired item found via image: {item} (conf={result[2]:.2f})")
                    found = True
                    
            if found:
                self.items_found[item] += 1
                found_in_this_screen.append(item)
                
        return found_in_this_screen

    def _check_logic(self, name, mandatory, optional, min_opt, inventory):
        """Helper to evaluate logic for a specific category (Treasure/Pet)."""
        if not mandatory and not optional:
            return True # Nothing requested for this category
            
        keep_mand = True
        if mandatory:
            for item in mandatory:
                if inventory.get(item, 0) > 0:
                    inventory[item] -= 1
                else:
                    keep_mand = False
                    break
            
        keep_opt = True
        if optional:
            opt_found = 0
            for item in optional:
                if inventory.get(item, 0) > 0:
                    inventory[item] -= 1
                    opt_found += 1
            keep_opt = opt_found >= min_opt
            
        keep = keep_mand and keep_opt
        
        if not keep:
            if mandatory and not keep_mand:
                logger.info(f"-> Failed: {name} missing mandatory items.")
            if optional and not keep_opt:
                logger.info(f"-> Failed: {name} not enough optional items (needed {min_opt}).")
                
        return keep

    def check_treasure_early(self):
        """Check if treasure criteria is met so far. Return False if we already failed."""
        if not self.treasure_mandatory and not self.treasure_optional:
            return True
            
        inventory_copy = self.items_found.copy()
        treasure_keep = self._check_logic("Treasure", self.treasure_mandatory, self.treasure_optional, self.treasure_min_opt, inventory_copy)
        
        if not treasure_keep:
            logger.warning("Early Evaluation: Treasure criteria NOT met! Skipping remaining draws.")
            return False
            
        return True

    def final_decision(self):
        """Make a keep/reroll decision based on mandatory and optional item logic."""
        if not self.all_target_items:
            logger.warning("No items configured to search for. Defaulting to reroll.")
            return False

        # Make a copy of the inventory so deductions don't affect other checks
        # (Though Treasure and Pet shouldn't overlap, it's safer)
        inventory_copy = self.items_found.copy()
        
        treasure_keep = self._check_logic("Treasure", self.treasure_mandatory, self.treasure_optional, self.treasure_min_opt, inventory_copy)
        pet_keep = self._check_logic("Pet", self.pet_mandatory, self.pet_optional, self.pet_min_opt, inventory_copy)

        keep = treasure_keep and pet_keep

        # Convert to normal dict for clean logging
        found_list = dict(self.items_found)
        if keep:
            logger.success(f"Session evaluation: KEEP account. Items found: {found_list}")
        else:
            logger.info(f"Session evaluation: REROLL. Items found: {found_list}")
            
        return keep
