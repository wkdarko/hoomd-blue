# Copyright (c) 2009-2021 The Regents of the University of Michigan
# This file is part of the HOOMD-blue project, released under the BSD 3-Clause
# License.

"""Implement AttachDataError."""


class AttachedDataError(RuntimeError):
    """Raised when data is inaccessible until the simulation is attached."""

    def __init__(self, data_name):
        self.data_name = data_name

    def __str__(self):
        """Returns the error message."""
        return f"The property {self.data_name} is unavailable until the"
        "simulation runs for 0 or more steps."
