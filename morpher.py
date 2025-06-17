import pymorphy3
from typing import Tuple, List, Optional, Dict

class SentenceMorpher:
    """Handles Ukrainian sentence and word morphing with advanced rule processing."""
    
    def __init__(self):
        self.morph = pymorphy3.MorphAnalyzer(lang='uk')
        self.supported_cases = ['nomn', 'gent', 'datv', 'accs', 'ablt', 'loct', 'voct']
        
    def _refine_dative_case(self, original_word: str, inflected_word: str) -> str:
        """
        Refines the dative case by preferring '-у'/'ю' endings over '-ові'/'-еві'/'єві'.
        It analyzes all possible lexeme forms to find the correct parallel form.
        Example: "стрільцеві" -> "стрільцю", "директорові" -> "директору".
        """
        if not inflected_word.endswith(('ові', 'еві', 'єві')):
            return inflected_word

        try:
            parsed_original = self.morph.parse(original_word)
            # Find a lexeme that matches the original word to get all its forms
            for p in parsed_original:
                if p.normal_form == parsed_original[0].normal_form:
                    # Search for a parallel dative form ending in 'у' or 'ю'
                    for form in p.lexeme:
                        if 'datv' in form.tag and (form.word.endswith('у') or form.word.endswith('ю')):
                            return form.word.capitalize() if original_word[0].isupper() else form.word
        except (AttributeError, IndexError):
            pass # If parsing fails, fall back to the original inflected word
            
        return inflected_word

    @staticmethod
    def _apply_patronymic_rules(word: str, case: str) -> str:
        """Applies post-processing rules specific to patronymics."""
        if not word:
            return ""

        # Rules for words ending in '-ич'
        if word.endswith('ич'):
            if case == 'datv':
                return word + 'у'
            if case == 'gent':
                return word + 'а'
            if case == 'ablt':
                return word + 'ем'
            if case == 'voct':
                return word + 'у'
        return word

    def morph_word(self, word: str, case: str, is_patronymic: bool = False) -> str:
        """
        Morphs a single word to a specified case with all post-processing.
        
        Args:
            word: Word to morph.
            case: Target grammatical case.
            is_patronymic: Flag for applying patronymic-specific rules.
            
        Returns:
            Morphed word or original if morphing fails.
        """
        try:
            is_capitalized = word and word[0].isupper()
            parsed = self.morph.parse(word)[0]
            inflected_word = parsed.inflect({case}).word
            
            # 1. Refine dative case endings (e.g., 'стрільцеві' -> 'стрільцю')
            if case == 'datv':
                inflected_word = self._refine_dative_case(word, inflected_word)
            
            # 2. Apply special rules for patronymics
            if is_patronymic:
                inflected_word = self._apply_patronymic_rules(inflected_word, case)
                
            return inflected_word.capitalize() if is_capitalized else inflected_word
        except (AttributeError, IndexError):
            return word

    def _process_position_part(self, words: List[str], case: str) -> List[str]:
        """Processes a part of a position title with special rules."""
        if not words:
            return []
            
        try:
            first_parsed = self.morph.parse(words[0])[0]
            is_adj = 'ADJF' in first_parsed.tag
        except (IndexError, AttributeError):
            is_adj = False
            
        # Heuristic: decline first word (noun) or first two (adj + noun)
        # The rest of the phrase is usually a chain of genitives and should not be touched.
        if is_adj and len(words) > 1:
            morphed_part = [
                self.morph_word(words[0], case),
                self.morph_word(words[1], case)
            ]
            morphed_part.extend(words[2:])
        else:
            morphed_part = [self.morph_word(words[0], case)]
            morphed_part.extend(words[1:])
        
        return morphed_part

    def morph_sentence(self, sentence: str, case: str, position: bool = False) -> str:
        """Morphs words in a sentence to a specified case."""
        if case not in self.supported_cases:
            raise ValueError(f"Unsupported case '{case}'. Use one of: {', '.join(self.supported_cases)}")
        if not sentence or not sentence.strip():
            return ''
            
        if not position:
            words = sentence.strip().split()
            return ' '.join(self.morph_word(w, case) for w in words)
        else:
            parts = [part.strip().split() for part in sentence.split(' - ')]
            processed_parts = [' '.join(self._process_position_part(p_words, case)) for p_words in parts]
            return ' - '.join(processed_parts)

class NameMorpher:
    """Handles Ukrainian name processing using the advanced SentenceMorpher engine."""
    
    def __init__(self, sentence_morpher: SentenceMorpher):
        self.morpher = sentence_morpher  # Use the sentence morpher as the engine
        self.morph = self.morpher.morph # Share the analyzer instance
        self.supported_cases = self.morpher.supported_cases
        self._case_cache: Dict[str, str] = {}
        
    def _inflect_name_part(self, name_part: str, case: str, is_patronymic: bool = False, is_feminine: bool = False) -> str:
        """Inflects a single name part using the shared morphing engine."""
        if not name_part:
            return ''

        cache_key = f"{name_part.lower()}_{case}_{is_patronymic}"
        if cache_key in self._case_cache:
            return self._case_cache[cache_key]

        # Rule for non-inflectable feminine surnames
        if is_feminine:
            try:
                parsed = self.morph.parse(name_part)[0]
                # Surnames that are also common nouns (Коваль, Ткач) or end in -ко, -ук are often not inflected for women
                if 'Sgtm' in parsed.tag and not any(name_part.endswith(s) for s in ['а', 'я']):
                    if case != 'nomn':
                        return name_part.capitalize()
            except (AttributeError, IndexError):
                pass
        
        # Use the powerful morph_word method from SentenceMorpher
        result = self.morpher.morph_word(name_part, case, is_patronymic=is_patronymic)
        self._case_cache[cache_key] = result
        return result

    def _determine_gender(self, first_name: str, patronymic: str = '') -> bool:
        """Determines if a name is feminine."""
        if patronymic and patronymic.lower().endswith(('івна', 'ївна')):
            return True
        if patronymic and patronymic.lower().endswith(('ич', 'ович')):
            return False
        if not first_name:
            return False
        try:
            return 'femn' in self.morph.parse(first_name)[0].tag
        except (AttributeError, IndexError):
            return False

    def morph_name(self, fullname: str, case: str = 'gent') -> str:
        """Processes a full name to a specified grammatical case."""
        if case not in self.supported_cases:
            raise ValueError(f"Unsupported case '{case}'. Use one of: {', '.join(self.supported_cases)}")
        if not fullname or not fullname.strip():
            return ''
        
        parts = fullname.strip().split()
        surname = parts[0] if parts else ''
        first_name = parts[1] if len(parts) > 1 else ''
        patronymic = parts[2] if len(parts) > 2 else ''
        
        is_feminine = self._determine_gender(first_name, patronymic)
        
        morphed_surname = self._inflect_name_part(surname, case, is_feminine=is_feminine)
        morphed_first_name = self._inflect_name_part(first_name, case, is_feminine=is_feminine)
        morphed_patronymic = self._inflect_name_part(patronymic, case, is_patronymic=True, is_feminine=is_feminine)
        
        # Final specific rule for names: uppercase surname
        final_parts = [morphed_surname.upper(), morphed_first_name, morphed_patronymic]
        
        return ' '.join(filter(None, final_parts))


class NameCLI:
    """Command line interface for name processing."""
    
    CASE_NAMES = {
        'nomn': "називний", 'gent': "родовий", 'datv': "давальний",
        'accs': "знахідний", 'ablt': "орудний", 'loct': "місцевий", 'voct': "кличний"
    }
    
    @staticmethod
    def run():
        """Runs the interactive CLI."""
        sentence_morpher = SentenceMorpher()
        name_processor = NameMorpher(sentence_morpher)
        
        print("Український універсальний відмінювач (версія 2.0)")
        print("1 - Відмінювання ПІБ")
        print("2 - Відмінювання речень/посад")
        print("Введіть 'вихід' або 'exit' для завершення")
        
        while True:
            try:
                mode = input("\nОберіть режим (1/2): ").strip().lower()
                if mode in ('вихід', 'exit'): break
                    
                print("\nДоступні відмінки:")
                for case, name in NameCLI.CASE_NAMES.items():
                    print(f"{case}: {name}")
                
                case = input("\nОберіть відмінок (скорочення): ").strip().lower()
                if case in ('вихід', 'exit'): break
                if case not in NameCLI.CASE_NAMES:
                    print("Невірний відмінок. Спробуйте ще раз.")
                    continue
                    
                if mode == '1':
                    fullname = input("Введіть ПІБ (Прізвище Ім'я По-батькові): ").strip()
                    if not fullname: continue
                    result = name_processor.morph_name(fullname, case)
                    print(f"{NameCLI.CASE_NAMES[case].capitalize()} відмінок: {result}")
                elif mode == '2':
                    text = input("Введіть речення або слово: ").strip()
                    if not text: continue
                    is_position_raw = input("Це посада? (так/ні, Enter=ні): ").strip().lower()
                    is_position = is_position_raw in ('т', 'так', 'y', 'yes')
                    result = sentence_morpher.morph_sentence(text, case, position=is_position)
                    print(f"{NameCLI.CASE_NAMES[case].capitalize()} відмінок: {result}")
                else:
                    print("Невірний режим. Спробуйте ще раз.")
                
            except (ValueError, IndexError) as e:
                print(f"Помилка: {e}")
            except Exception as e:
                print(f"Неочікувана помилка: {type(e).__name__}: {e}")

if __name__ == "__main__":
    NameCLI.run()