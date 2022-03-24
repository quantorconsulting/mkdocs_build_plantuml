from setuptools import setup, find_packages

setup(
    name='mkdocs-build-plantuml-plugin',
    version='1.7.0',
    description='An MkDocs plugin to call plantuml locally or remote',
    long_description='',
    keywords='mkdocs plantuml publishing documentation uml sequence diagram',
    url='https://github.com/christo-ph/mkdocs_build_plantuml',
    author='Christoph Galler',
    author_email='galler@quantor.com',
    license='MIT',
    python_requires='>=3.2',
    install_requires=[
        'mkdocs>=1.0.4', 'httplib2'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
    ],
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests", "example"]),
    entry_points={
        'mkdocs.plugins': [
            'build_plantuml = mkdocs_build_plantuml_plugin.plantuml:BuildPlantumlPlugin'
        ]
    }
)
