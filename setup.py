from setuptools import find_packages, setup

setup(
    name='superofficesdk',
    packages=find_packages(),
    version='1.0.6',
    description='SuperOffice Python SDK',
    package_data={'superofficesdk': ['PartnerSystemUserService.wsdl']},
    include_package_data=True, 
    author='Anthony De Smet',
    license='MIT'
)