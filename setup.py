import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="gsec",
	version="0.0.1",
	# For calling the script
	entry_points={
		"console_scripts": [
			'gsec = gsec.gsec:main',
			'gsec_train = gsec.gsec_train:main',
		]
	},
	author="Isaac Gelman, Nicolas Perez, Natalie Abreu, Shannon Brownlee, \
	Tomas Angelini, Laura Cao, Shreya Havaldar",
	description="Automated, generalizable model building tool \
	for the Sequence Read Archive",
	long_description=long_description,
	url="https://github.com/gelman-usc/gsec",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3"
	],
	python_requires=">=3.6",
	install_requires=[
		"pandas",
		"sklearn",
		"numpy",
	]
)
