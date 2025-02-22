from django.core.cache import cache


async def save_otp_to_cache(telegram_id, otp):
    cache.set(f'otp_email_verification_{telegram_id}', otp, time=300)


async def get_otp_from_cache(telegram_id):
    return cache.get(f'otp_email_verification_{telegram_id}')
