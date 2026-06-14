from setuptools import setup, find_packages

setup(
    name="bm-address",
    version="0.1.0",
    description="Expand abbreviated Malaysian addresses for display and text-to-speech.",
    long_description=(
        "bm-address expands common Malaysian address abbreviations "
        "(JLN, KG, TMN, BKT, KL, PJ, ...) to their full form and produces "
        "syllabified output suitable for text-to-speech."
    ),
    long_description_content_type="text/plain",
    url="https://github.com/your-org/bm-address-normaliser",
    license="MIT",
    packages=find_packages(exclude=("tests",)),
    python_requires=">=3.9",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Text Processing :: Linguistic",
        "Natural Language :: Malay",
    ],
    keywords=["malaysia", "address", "normalise", "tts", "bahasa-malaysia"],
)
