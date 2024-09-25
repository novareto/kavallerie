CHANGES
=======

0.5.2 (2024-09-25)
------------------

 * py3.12 compatibility ensured with importlib-metadata update for the
   plugins entrypoints.


0.5.1 (2023-09-25)
------------------

  * Fixed `security_bypass` auth filter using `pathlib.PurePosixPath`


0.5 (2023-06-12)
----------------

  * Removed `unique` decorator to use `functools.cached_property`
  * Decoupled the ordering of the pipeline items into a reusable
    baseclass called `PriorityChain`


0.4 (2022-10-12)
----------------

  * `Request` no longer takes path as an arg.
    It uses the environ to compute.
  * Added `Request` abstract class to implement non WSGI requests.
  * Using `gelidum` instead of `frozen_box`


0.3 (2022-08-25)
----------------

  * Based on the changes of `Horseman` 0.6 : the `FormData`,
    `TypeCastingDict` and `Query` classes were moved in-house.

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
