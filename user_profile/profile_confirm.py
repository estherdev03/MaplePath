from states.graph_states import UserState
from states.profile_states import UserProfile


def profile_confirm(state: UserState):
    payload = state.event.payload
    profile = UserProfile(
        age=payload.age,
        job_title=payload.job_title,
        languages=payload.languages,
        work_experience=payload.work_experience,
    )
    return {"profile": profile}
