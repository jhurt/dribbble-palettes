from distutils.core import setup

setup(
    name='dribbble_palettes',
    packages=['dribbble_palettes'],
    install_requires=[
        "Pillow==2.7.0",
        "Scrapy==1.0.3",
    ],
    entry_points={
        'console_scripts': [
            'palette_from_color = dribbble_palettes.palette_from_color:cli',
        ]
    }
)
