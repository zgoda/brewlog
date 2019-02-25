from ..ext import db


def update_steps_gravity(step):
    if step.fg is not None:
        next_step = step.next_step()
        if next_step:
            next_step.og = step.fg
            db.session.add(next_step)
