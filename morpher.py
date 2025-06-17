"""
A comprehensive Ukrainian language morphology tool for inflecting names,
positions, and sentences, built on top of pymorphy3.

This module provides three main classes:
- SentenceMorpher: The core engine for word and sentence inflection with advanced rules.
- NameMorpher: A specialized class for handling Ukrainian full names (ПІБ).
- NameCLI: A command-line interface to interact with the morphing tools.
"""
import pymorphy3
from typing import List, Dict

# --- Core Morphology Engine ---

class SentenceMorpher:
    """
    Handles Ukrainian sentence and word morphing with advanced rule processing.
    This class is the main engine that performs inflection using pymorphy3
    and applies custom, fine-tuned rules for Ukrainian.
    """
    
    def __init__(self):
        """Initializes the morph analyzer for the Ukrainian language."""
        self.morph = pymorphy3.MorphAnalyzer(lang='uk')
        self.supported_cases = {'nomn', 'gent', 'datv', 'accs', 'ablt', 'loct', 'voct'}
        
    def _refine_dative_case(self, original_word: str, inflected_word: str) -> str:
        """
        Refines the dative case by preferring '-у'/'ю' endings over '-ові'/'-еві'/'єві'.

        In Ukrainian, many masculine nouns have parallel dative forms (e.g.,
        "директору" and "директорові"). This method standardizes the output by
        choosing the shorter form, which is often preferred in official documents.

        Args:
            original_word: The word in its original (nominative) form.
            inflected_word: The word inflected by pymorphy3, which might have an '-ові' ending.

        Returns:
            The refined dative form of the word, preferably ending in '-у' or '-ю'.
        """
        # If the default inflection doesn't end in -ові/-еві/-єві, no refinement is needed.
        if not inflected_word.endswith(('ові', 'еві', 'єві')):
            return inflected_word

        try:
            # Parse the original word to access its entire lexeme (all possible forms).
            parsed_original = self.morph.parse(original_word)
            if not parsed_original:
                return inflected_word
            
            # We assume the first parse is the correct one for finding the lexeme.
            target_lexeme = parsed_original[0].lexeme
            
            # Search for a parallel dative form in the lexeme that ends in 'у' or 'ю'.
            for form in target_lexeme:
                if 'datv' in form.tag and (form.word.endswith('у') or form.word.endswith('ю')):
                    # Preserve capitalization of the original word.
                    return form.word.capitalize() if original_word and original_word[0].isupper() else form.word
        except (AttributeError, IndexError):
            # If parsing or lexeme analysis fails, fall back to the initial inflected word.
            pass
            
        return inflected_word

    def morph_word(self, word: str, case: str) -> str:
        """
        Morphs a single word to a specified case with all post-processing.
        
        Args:
            word: The word to morph.
            case: The target grammatical case (e.g., 'gent', 'datv').
            
        Returns:
            The morphed word, or the original word if morphing fails.
        """
        if not word or not case:
            return word

        try:
            is_capitalized = word[0].isupper()
            parsed = self.morph.parse(word)[0]
            
            inflected = parsed.inflect({case})
            # If pymorphy3 can't form the case, it returns None.
            if inflected is None:
                return word
            
            inflected_word = inflected.word
            
            # Rule 1: Refine dative case endings (e.g., 'директорові' -> 'директору').
            if case == 'datv':
                inflected_word = self._refine_dative_case(word, inflected_word)
                
            return inflected_word.capitalize() if is_capitalized else inflected_word
        except (AttributeError, IndexError, TypeError):
            # Fallback to the original word in case of any parsing/inflection error.
            return word

    def _process_position_part(self, words: List[str], case: str) -> List[str]:
        """
        Processes a part of a position title with special rules.
        
        Heuristic: In Ukrainian job titles like "Головний спеціаліст відділу кадрів",
        only the core position ("Головний спеціаліст") is inflected. The rest of the
        phrase often consists of nouns in the genitive case that should not be changed.
        This method inflects the first one or two words and leaves the rest as is.
        """
        if not words:
            return []
            
        try:
            # Check if the first word is an adjective ('ADJF').
            first_parsed = self.morph.parse(words[0])[0]
            is_adj = 'ADJF' in first_parsed.tag
        except (IndexError, AttributeError):
            is_adj = False
            
        # If the phrase starts with an adjective and has a following noun, inflect both.
        if is_adj and len(words) > 1:
            morphed_part = [
                self.morph_word(words[0], case),
                self.morph_word(words[1], case)
            ]
            morphed_part.extend(words[2:])
        else: # Otherwise, inflect only the first word (assumed to be a noun).
            morphed_part = [self.morph_word(words[0], case)]
            morphed_part.extend(words[1:])
        
        return morphed_part

    def morph_sentence(self, sentence: str, case: str, is_position: bool = False) -> str:
        """
        Morphs words in a sentence or a position title to a specified case.

        Args:
            sentence: The text to morph.
            case: The target grammatical case.
            is_position: If True, applies special rules for job titles.

        Returns:
            The morphed sentence.
        
        Raises:
            ValueError: If the case is not supported.
        """
        if case not in self.supported_cases:
            raise ValueError(f"Unsupported case '{case}'. Use one of: {', '.join(self.supported_cases)}")
        if not sentence.strip():
            return ''
            
        if not is_position:
            words = sentence.strip().split()
            morphed_words = [self.morph_word(w, case) for w in words]
            return ' '.join(morphed_words)
        else:
            # Positions can be complex, e.g., "Посада1 - Посада2". Process each part separately.
            parts = [part.strip().split() for part in sentence.split(' - ')]
            processed_parts = [' '.join(self._process_position_part(p_words, case)) for p_words in parts]
            return ' - '.join(processed_parts)

# --- Name Processing Wrapper ---

class NameMorpher:
    """
    Handles Ukrainian full name (ПІБ) processing using the SentenceMorpher engine.
    This class adds name-specific logic, such as gender detection and rules for
    inflecting or not inflecting feminine surnames.
    """
    
    def __init__(self, sentence_morpher: SentenceMorpher):
        """
        Initializes the NameMorpher with a SentenceMorpher instance.

        Args:
            sentence_morpher: An instance of SentenceMorpher to use as the morphing engine.
        """
        self.morpher = sentence_morpher
        self.morph = self.morpher.morph  # Share the pymorphy3 analyzer instance
        self.supported_cases = self.morpher.supported_cases
        self._case_cache: Dict[str, str] = {}
        
    def _inflect_name_part(self, name_part: str, case: str, is_feminine: bool = False) -> str:
        """
        Inflects a single part of a name (e.g., surname, first name) with caching.

        Args:
            name_part: The part of the name to inflect.
            case: The target grammatical case.
            is_feminine: A flag indicating if the name is feminine, used for special rules.

        Returns:
            The inflected name part.
        """
        if not name_part:
            return ''

        # The cache key must be unique for the word, case, and gender context.
        cache_key = f"{name_part.lower()}_{case}_{is_feminine}"
        if cache_key in self._case_cache:
            return self._case_cache[cache_key]

        # Special rule for feminine surnames that are not inflected.
        # This applies to surnames that look like common nouns (e.g., Ткач, Коваль)
        # or end in consonants or -ко, -ук, etc.
        if is_feminine:
            try:
                parsed = self.morph.parse(name_part)[0]
                # 'Sgtm' is a tag for surname. Surnames not ending in 'а'/'я' are usually not inflected for women.
                if 'Sgtm' in parsed.tag and not name_part.endswith(('а', 'я')):
                    if case != 'nomn':
                        # Preserve original capitalization
                        result = name_part.capitalize() if name_part and name_part[0].isupper() else name_part
                        self._case_cache[cache_key] = result
                        return result
            except (AttributeError, IndexError):
                pass
        
        # Use the powerful morph_word method from SentenceMorpher for actual inflection.
        result = self.morpher.morph_word(name_part, case)
        self._case_cache[cache_key] = result
        return result

    def _determine_gender(self, first_name: str, patronymic: str) -> bool:
        """

        Determines if a full name is feminine based on patronymic or first name.
        """
        # Patronymic is the most reliable indicator of gender.
        patronymic_lower = patronymic.lower()
        if patronymic_lower.endswith(('івна', 'ївна')):
            return True
        if patronymic_lower.endswith(('ич', 'ович')):
            return False
            
        # If no patronymic, fall back to analyzing the first name.
        if not first_name:
            return False
        try:
            # 'femn' tag indicates a feminine name.
            return 'femn' in self.morph.parse(first_name)[0].tag
        except (AttributeError, IndexError):
            # Default to masculine if parsing fails.
            return False

    def morph_name(self, fullname: str, case: str = 'gent', uppercase_surname: bool = True) -> str:
        """
        Processes a full name (ПІБ) to a specified grammatical case.

        Args:
            fullname: The full name string, e.g., "Шевченко Тарас Григорович".
            case: The target case, defaults to 'gent' (genitive).
            uppercase_surname: If True, the surname in the output will be uppercased.

        Returns:
            The morphed full name as a string.
        """
        if case not in self.supported_cases:
            raise ValueError(f"Unsupported case '{case}'. Use one of: {', '.join(self.supported_cases)}")
        if not fullname.strip():
            return ''
        
        parts = fullname.strip().split()
        surname = parts[0] if len(parts) > 0 else ''
        first_name = parts[1] if len(parts) > 1 else ''
        patronymic = parts[2] if len(parts) > 2 else ''
        
        is_feminine = self._determine_gender(first_name, patronymic)
        
        morphed_surname = self._inflect_name_part(surname, case, is_feminine=is_feminine)
        morphed_first_name = self._inflect_name_part(first_name, case, is_feminine=is_feminine)
        morphed_patronymic = self._inflect_name_part(patronymic, case, is_feminine=is_feminine)
        
        # Apply optional formatting rule for the surname.
        if uppercase_surname:
            morphed_surname = morphed_surname.upper()

        final_parts = [morphed_surname, morphed_first_name, morphed_patronymic]
        
        return ' '.join(filter(None, final_parts))


# --- Command-Line Interface ---

class NameCLI:
    """Command line interface for name and sentence processing."""
    
    CASE_NAMES = {
        'nomn': "Називний", 'gent': "Родовий", 'datv': "Давальний",
        'accs': "Знахідний", 'ablt': "Орудний", 'loct': "Місцевий", 'voct': "Кличний"
    }
    
    @staticmethod
    def run():
        """Runs the interactive command-line interface."""
        # Initialize the core components
        sentence_morpher = SentenceMorpher()
        name_processor = NameMorpher(sentence_morpher)
        
        print("--- Український універсальний відмінювач (v2.0) ---")
        print("1 - Відмінювання ПІБ")
        print("2 - Відмінювання речень / посад")
        print("Введіть 'вихід' або 'exit' для завершення.")
        
        while True:
            try:
                mode = input("\nОберіть режим (1/2): ").strip().lower()
                if mode in ('вихід', 'exit'):
                    break
                    
                if mode not in ('1', '2'):
                    print("Невірний режим. Будь ласка, введіть 1 або 2.")
                    continue
                
                print("\nДоступні відмінки:")
                for code, name in NameCLI.CASE_NAMES.items():
                    print(f"  {code:<5} - {name}")
                
                case = input("\nОберіть відмінок (напр., 'gent'): ").strip().lower()
                if case in ('вихід', 'exit'):
                    break
                if case not in NameCLI.CASE_NAMES:
                    print("Невірний код відмінка. Спробуйте ще раз.")
                    continue
                    
                if mode == '1':
                    fullname = input("Введіть ПІБ (Прізвище Ім'я По-батькові): ").strip()
                    if not fullname: continue
                    result = name_processor.morph_name(fullname, case)
                    print(f"-> {NameCLI.CASE_NAMES[case]} відмінок: {result}")
                elif mode == '2':
                    text = input("Введіть речення або посаду: ").strip()
                    if not text: continue
                    is_position_raw = input("Це посада? (так/ні, Enter=ні): ").strip().lower()
                    is_position = is_position_raw in ('т', 'так', 'y', 'yes')
                    result = sentence_morpher.morph_sentence(text, case, is_position=is_position)
                    print(f"-> {NameCLI.CASE_NAMES[case]} відмінок: {result}")
                
            except (ValueError, IndexError) as e:
                print(f"Помилка: {e}")
            except (KeyboardInterrupt, EOFError):
                print("\nЗавершення роботи.")
                break
            except Exception as e:
                print(f"Неочікувана помилка: {type(e).__name__}: {e}")

if __name__ == "__main__":
    NameCLI.run()
