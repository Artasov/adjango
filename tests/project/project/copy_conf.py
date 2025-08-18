# config/copy_conf.py
configurations = {
    #######################
    #         BASE        #
    #######################
    "base": {
        "__start_dir__": r"F:\dev",  # optional, defaults to BASE_DIR if not specified
        "__exclude__": [
            "__init__",
            "pycache",
            ".pyc",
        ],
        "__add_paths__": True,
        "adjango": {
            "adjango": {
                "constants": "__copy__",
                "exceptions": "__copy__",
                "management": "__copy__",
                "managers": "__copy__",
                "models": "__copy__",
                "querysets": "__copy__",
                "services": "__copy__",
                "utils": "__copy__",
                "conf": "__copy__",
                "adecorators": "__copy__",
                "decorators": "__copy__",
                "aserializers": "__copy__",
                "serializers": "__copy__",
                "fields": "__copy__",
                "handlers": "__copy__",
                "middleware": "__copy__",
                "tasks": "__copy__",
                "testing": "__copy__",
            },
            "README": "__copy__",
        },
    },
    "wide-containers": {
        "__start_dir__": r"F:\dev\wide-containers",  # optional, defaults to BASE_DIR if not specified
        "__exclude__": [
            "__init__",
            "pycache",
            ".pyc",
        ],
        "__add_paths__": True,
        "src": "__copy__",
        "package": "__copy__",
        "tsconfig": "__copy__",
        "webpack.config": "__copy__",
    },
}
