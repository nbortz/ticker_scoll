import sys
import time
import requests
import pygame

#Configuration
TICKERS = [('bitcoin', 'BTC'),
          ('ethereum', 'ETH'),
          ('solana', 'SOL'),
          ('hyperliquid', 'HYPE'),
          ('dogecoin', 'DOGE'),
          ('chainlink', 'LINK'),
          ('zcash', 'ZEC'),
          ('pendle', 'PENDLE'),
          ('fartcoin', 'FARTCOIN')]

VS_CURRENCY = 'usd'
FETCH_INTERVAL = 30
SCROLL_SPEED = 2

#pygame setup

pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Crypto Ticker")
font = pygame.font.SysFont(None, 64)
clock = pygame.time.Clock()

def fetchPrices():
    ids = ','.join([t[0] for t in TICKERS])
    url = 'https://api.coingecko.com/api/v3/simple/price'
    params = {
        'ids':ids,
        'vs_currencies':VS_CURRENCY,
        'include_24hr_change':'true'
    }
    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error fetching prices: {e}")
        return {}

def build_ticker_surface(data):
    font = pygame.font.SysFont("Courier New", 112)
    parts = []
    total_width = 0
    heights = []

    # Render each coin's text with its own color
    for coin_id, sym in TICKERS:
        info = data.get(coin_id, {})
        raw_price  = info.get(VS_CURRENCY)
        raw_change = info.get(f'{VS_CURRENCY}_24h_change')
        price  = raw_price  if raw_price  is not None else 0.0
        change = raw_change if raw_change is not None else 0.0

        if change > 0:
            color = 'green'
        elif change < 0:
            color = 'red'
        else:
            color = 'white'

        text = f"{sym}:{price:,.0f} {change:+.2f}%   "
        surf = font.render(text, True, pygame.Color(color))
        parts.append(surf)
        total_width += surf.get_width()
        heights.append(surf.get_height())

    # Create a surface wide enough for all parts
    ticker_surface = pygame.Surface((total_width, max(heights)), pygame.SRCALPHA)
    x = 0
    for surf in parts:
        ticker_surface.blit(surf, (x, 0))
        x += surf.get_width()

    return ticker_surface

def main():
    next_fetch = 0
    ticker_surf = None
    text_width = 0
    x = WIDTH

    running = True
    while running:
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT or \
                (evt.type == pygame.KEYDOWN and evt.key == pygame.K_ESCAPE):
                running = False

        now = time.time()
        if now >= next_fetch or ticker_surf is None:
            data = fetchPrices()
            ticker_surf = build_ticker_surface(data)
            text_width = ticker_surf.get_width()
            next_fetch = now + FETCH_INTERVAL
            # Do NOT reset x here

        screen.fill(pygame.Color('black'))
        screen.blit(ticker_surf, (x, (HEIGHT - ticker_surf.get_height()) // 2))
        pygame.display.flip()

        x -= SCROLL_SPEED
        if x < -text_width:
            x = WIDTH  # Only reset x when the ticker has fully scrolled off

        clock.tick(90)
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()