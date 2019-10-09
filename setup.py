from setuptools import setup, find_packages


def scm_version():
    def local_scheme(version):
        return version.format_choice("+{node}", "+{node}.dirty")
    return {
        "relative_to": __file__,
        "version_scheme": "guess-next-dev",
        "local_scheme": local_scheme
    }


setup(
    name="lambdausb",
    use_scm_version=scm_version(),
    author="Jean-François Nguyen",
    author_email="jf@lambdaconcept.com",
    description="A configurable USB 2.0 device core",
    license="BSD",
    python_requires="~=3.6",
    setup_requires=["setuptools_scm"],
    install_requires=["setuptools", "nmigen"],
    packages=find_packages(),
    project_urls={
        "Source Code": "https://github.com/lambdaconcept/lambdausb",
        "Bug Tracker": "https://github.com/lambdaconcept/lambdausb/issues",
    },
)
