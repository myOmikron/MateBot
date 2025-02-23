"""
MateBot router module for /aliases requests
"""

import logging
from typing import List

import pydantic
from fastapi import APIRouter, Depends

from ..base import Conflict, NotFound
from ..dependency import LocalRequestData
from .. import helpers
from ...persistence import models
from ... import schemas


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/aliases",
    tags=["Aliases"]
)


@router.get(
    "",
    response_model=List[schemas.Alias]
)
def get_all_known_aliases(local: LocalRequestData = Depends(LocalRequestData)):
    """
    Return a list of all known user aliases of all applications.
    """

    return helpers.get_all_of_model(models.UserAlias, local)


@router.post(
    "",
    status_code=201,
    response_model=schemas.Alias,
    responses={404: {"model": schemas.APIError}, 409: {"model": schemas.APIError}}
)
def create_new_alias(
        alias: schemas.AliasCreation,
        local: LocalRequestData = Depends(LocalRequestData)
):
    """
    Create a new alias if no combination of `app_user_id` and `application` exists.

    The `app_user_id` field should reflect the unique internal username in the
    frontend application and may be any string with a maximum length of 255 chars.

    A 404 error will be returned if the `user_id` or `application` is not known.
    A 409 error will be returned when the combination of those already exists.
    """

    user = helpers.return_one(alias.user_id, models.User, local.session)
    application = helpers.return_unique(models.Application, local.session, name=alias.application)

    existing_alias = local.session.query(models.UserAlias).filter_by(
        app_id=application.id,
        app_user_id=alias.app_user_id
    ).first()
    if existing_alias is not None:
        raise Conflict(
            "User alias can't be created since it already exists.",
            f"Alias: {existing_alias!r}"
        )

    model = models.UserAlias(
        user_id=user.id,
        app_id=application.id,
        app_user_id=alias.app_user_id
    )
    return helpers.create_new_of_model(model, local, logger)


@router.put(
    "",
    response_model=schemas.Alias,
    responses={404: {"model": schemas.APIError}, 409: {"model": schemas.APIError}}
)
def update_existing_alias(
        alias: schemas.Alias,
        local: LocalRequestData = Depends(LocalRequestData)
):
    """
    Update an existing alias model identified by the `alias_id`.

    It's also possible to overwrite the previous unique
    `app_user_id` of that `alias_id` to adapt to changes.
    It's not possible to change the `application` or
    `user_id` fields, compared to the server state.

    A 404 error will be returned if the `alias_id` doesn't exist.
    A 409 error will be returned when the combination of `app_user_id`
    and `application` already exists with another alias.
    """

    alias_model = helpers.return_one(alias.id, models.UserAlias, local.session)
    user = helpers.return_one(alias.user_id, models.User, local.session)
    application = helpers.return_unique(models.Application, local.session, name=alias.application)

    alias_model.user_id = user.id
    alias_model.app_id = application.id
    alias_model.app_user_id = alias.app_user_id

    local.session.add(alias_model)
    local.session.commit()
    return helpers.get_one_of_model(alias.id, models.UserAlias, local)


@router.delete(
    "",
    status_code=204,
    responses={
        404: {"model": schemas.APIError},
        409: {"model": schemas.APIError},
        412: {"model": schemas.APIError}
    }
)
def delete_existing_alias(
        alias: schemas.Alias,
        local: LocalRequestData = Depends(LocalRequestData)
):
    """
    Delete an existing alias model.

    A 404 error will be returned if the requested `id` doesn't exist.
    A 409 error will be returned if the object is not up-to-date, which
    means that the user agent needs to get the object before proceeding.
    A 412 error will be returned if the conditional request fails.
    """

    helpers.delete_one_of_model(
        alias.id,
        models.UserAlias,
        local,
        schema=alias,
        logger=logger
    )


@router.get(
    "/{alias_id}",
    response_model=schemas.Alias,
    responses={404: {"model": schemas.APIError}}
)
def get_alias_by_id(
        alias_id: pydantic.NonNegativeInt,
        local: LocalRequestData = Depends(LocalRequestData)
):
    """
    Return the alias model of a specific alias ID.

    A 404 error will be returned in case the alias ID is unknown.
    """

    return helpers.get_one_of_model(alias_id, models.UserAlias, local)


@router.get(
    "/application/{application}",
    response_model=List[schemas.Alias],
    responses={404: {"model": schemas.APIError}}
)
def get_aliases_by_application_name(
        application: pydantic.constr(max_length=255),
        local: LocalRequestData = Depends(LocalRequestData)
):
    """
    Return a list of all users aliases for a given application name.

    A 404 error will be returned for unknown `application` arguments.
    """

    app = local.session.query(models.Application).filter_by(name=application).first()
    if app is None:
        raise NotFound(f"Application name {application!r}")
    return helpers.get_all_of_model(models.UserAlias, local, app_id=app.id)
