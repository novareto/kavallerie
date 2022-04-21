CHANGES
=======

0.2.1 (2022-04-21)
------------------

  * Request now handles possible incorrect WSGI environ with empty key
    values, such as `REQUEST_METHOD`, `SCRIPT_NAME` or `QUERY_STRING`.

0.2 (2022-04-05)
----------------

  * Added handling of empty path as it can occur in different scenarios.
    WSGI can provide an empty PATH_INFO or Horseman `Mapping` can match
    script_name that eats up the whole path.

0.1 (2022-03-29)
----------------

  * Initial release.
