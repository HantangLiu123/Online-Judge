from enum import Enum
from datetime import date
from tortoise import fields, models

class UserRole(str, Enum):

    """three status for a user's role"""

    USER = 'user'
    ADMIN = 'admin'
    BANNED = 'banned'

def get_current_date():
    return date.today()

class User(models.Model):

    """a model for a user"""

    id = fields.IntField(primary_key=True)
    username = fields.CharField(max_length=40, null=False, unique=True)
    password = fields.CharField(max_length=200, null=False)
    role = fields.CharEnumField(UserRole, default=UserRole.USER, null=False)
    join_time = fields.DateField(default=get_current_date)
    submit_count = fields.IntField(default=0)
    resolve_count = fields.IntField(default=0)
    submissions = fields.ReverseRelation['Submission']
    resolves = fields.ReverseRelation['Resolve']

class Difficulty(str, Enum):

    """three difficulties of problems"""

    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'

class Problem(models.Model):

    """a model for a problem"""

    id=fields.CharField(primary_key=True, max_length=50, null=False)
    title=fields.CharField(max_length=50, null=False)
    description = fields.TextField(null=False)
    input_description = fields.TextField(null=False)
    output_description = fields.TextField(null=False)
    samples = fields.JSONField(null=False)
    constraints = fields.TextField(null=False)
    testcases = fields.JSONField(null=False)

    hint = fields.TextField(null=True)
    source = fields.CharField(max_length=20, null=True)
    tags = fields.JSONField(null=True)
    time_limit = fields.FloatField(null=True)
    memory_limit = fields.IntField(null=True)
    author = fields.CharField(max_length=50, null=True)
    difficulty = fields.CharEnumField(Difficulty, default=Difficulty.MEDIUM)

    submissions = fields.ReverseRelation['Submission']
    resolves = fields.ReverseRelation['Resolve']

class SubmissionStatus(str, Enum):

    """the status for a submission"""

    PENDING = 'pending'
    SUCCESS = 'success'
    ERROR = 'error'

class Submission(models.Model):

    """a model for a submission"""

    id = fields.IntField(primary_key=True)
    submission_id = fields.UUIDField(unique=True)
    user = fields.ForeignKeyField(
        model_name='models.User',
        related_name='submissions',
        on_delete=fields.OnDelete.CASCADE,
    )
    problem = fields.ForeignKeyField(
        model_name='models.Problem',
        related_name='submissions',
        on_delete=fields.OnDelete.CASCADE,
    )
    submission_time = fields.DatetimeField()
    language = fields.CharField(max_length=20, null=False)
    status = fields.CharEnumField(SubmissionStatus)
    score = fields.IntField(null=True)
    counts = fields.IntField(null=True)
    code = fields.TextField(null=False)
    tests = fields.ReverseRelation['Test']

class TestResult(str, Enum):

    """possible results of a test"""

    AC = 'AC'
    WA = 'WA'
    RE = 'RE'
    CE = 'CE'
    TLE = 'TLE'
    MLE = 'MLE'
    UNK = 'UNK'

class Test(models.Model):

    """a model for a testcase of a submission"""

    test_id = fields.IntField(null=False)
    submission = fields.ForeignKeyField(
        model_name='models.Submission',
        related_name='tests',
        on_delete=fields.OnDelete.CASCADE,
    )
    result = fields.CharEnumField(TestResult)
    time = fields.FloatField(null=False)
    memory = fields.IntField(null=False)

class Resolve(models.Model):

    """record whether the user has resolved a problem with a specific language"""

    problem = fields.ForeignKeyField(
        model_name='models.Problem',
        related_name='resolves',
        on_delete=fields.OnDelete.CASCADE,
    )
    user = fields.ForeignKeyField(
        model_name='models.User',
        related_name='resolves',
        on_delete=fields.OnDelete.CASCADE,
    )
    language = fields.CharField(max_length=15, null=False)
    resolved = fields.BooleanField(null=False)

class Language(models.Model):

    """a model for a supported language"""

    name = fields.CharField(max_length=15, null=False, unique=True)
    file_ext = fields.CharField(max_length=5, null=False)
    compile_cmd = fields.CharField(max_length=50, null=True)
    run_cmd = fields.CharField(max_length=20, null=False)
    time_limit = fields.FloatField(null=False)
    memory_limit = fields.IntField(null=False)
    image_name = fields.CharField(max_length=50, null=False)
