CHANGES
=======

1.0a9 (2026-04-21)
------------------

 * Fixed wrong `source_id` in `identify`.


1.0a8 (2026-03-30)
------------------

 * Unsuccessful auth now returns "None" only, not a tuple.


1.0a7 (2026-03-30)
------------------

 * `ResolvedUser` is now returned as a User wrapping proxy to account
   for the source_id.


1.0a6 (2026-03-27)
------------------

 * `Request` now respects the `RequestProtocol` from `authsources`


1.0a4 (2026-03-25)
------------------

 * Added `HTTPError` handling in the application.


1.0a3 (2026-03-25)
------------------

 * Added `FlagsField` to the request.


1.0a2 (2026-03-24)
------------------

 * Fixed `horseman` HTTPError import.


1.0a1 (2026-03-24)
------------------

 * Using latest `horseman`.
 * Backported `roughrider.routing` and `roughrider.cors`.
 * Overall streamlining.


0.7 (2026-02-23)
----------------

 * Sources are now named and are more advanced.
   The authentication returns the source id where the user was found.
   This requires a migration from previous versions.


0.6 (2024-10-17)
----------------

 * The emailer can now send email with attachments.


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
