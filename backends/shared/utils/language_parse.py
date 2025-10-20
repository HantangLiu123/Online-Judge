from ..models import Language
from ..schemas import LanguageSchema

def language_schema_to_language(lan: LanguageSchema) -> Language:

    """parse language schema to language"""

    lan_dict = lan.model_dump()
    return Language(**lan_dict)

def language_to_language_schema(language: Language) -> LanguageSchema:

    """parse language to language schema"""

    return LanguageSchema(
        name=language.name,
        file_ext=language.file_ext,
        compile_cmd=language.compile_cmd,
        run_cmd=language.run_cmd,
        time_limit=language.time_limit,
        memory_limit=language.memory_limit,
        image_name=language.image_name,
    )
