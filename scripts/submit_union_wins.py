#!/usr/bin/env python3
"""
Script to submit union win URLs to the UnionWins submission endpoint.
Submits each URL with a 10-second delay between submissions.
"""
import requests
import time
import sys

# Base URL for the API
BASE_URL = "http://localhost:3001"
SUBMISSION_ENDPOINT = f"{BASE_URL}/api/submissions"
DELAY_SECONDS = 0.5

# List of URLs to submit
URLS = [
    "https://www.unitetheunion.org/news-events/news/2025/december/dhl-strikes-at-luton-airport-off-after-improved-offer",
    "https://www.unitetheunion.org/news-events/news/2025/december/strikes-at-shelter-off-as-workers-accept-new-working-hours-deal",
    "https://www.unitetheunion.org/news-events/news/2025/december/metrolink-tram-driver-strikes-off-as-workers-accept-deal-to-tackle-fatigue",
    "https://www.unitetheunion.org/news-events/news/2025/december/newham-mental-health-staff-celebrate-newly-won-pay-and-conditions",
    "https://www.unitetheunion.org/news-events/news/2025/december/arriva-leicestershire-strikes-off-after-unite-wins-improved-pay-offer",
    "https://www.unitetheunion.org/news-events/news/2025/december/first-aberdeen-drivers-and-staff-celebrate-early-pay-increase",
    "https://www.unitetheunion.org/news-events/news/2025/december/strikes-at-diageo-belfast-suspended-after-improved-pay-offer",
    "https://www.unitetheunion.org/news-events/news/2025/december/welsh-bus-workers-celebrate-significant-pay-win-after-strike-action",
    "https://www.unitetheunion.org/news-events/news/2025/november/pay-win-delivered-for-gxo-logistics-drivers-in-motherwell",
    "https://www.unitetheunion.org/news-events/news/2025/november/bank-of-england-security-strike-off-as-workers-accept-excellent-deal",
    "https://www.unitetheunion.org/news-events/news/2025/november/leonardo-workers-achieve-pay-increase-deal",
    "https://www.unitetheunion.org/news-events/news/2025/november/imperial-college-union-membership-grows-as-strike-escalates",
    "https://www.unitetheunion.org/news-events/news/2025/november/unite-members-win-high-court-victory-in-pay-battle-with-bae-systems",
    "https://www.unitetheunion.org/news-events/news/2025/november/immingham-db-cargo-workers-celebrate-11-700-pay-victory-secured-by-unite",
    "https://www.unitetheunion.org/news-events/news/2025/october/unite-secures-pay-rise-for-offshore-altrad-workers-on-enquest-s-magnus-and-thistle-alpha-platforms",
    "https://www.unitetheunion.org/news-events/news/2025/october/lufthansa-technik-workers-in-hayes-celebrate-pay-victory",
    "https://www.unitetheunion.org/news-events/news/2025/october/hospitality-workers-at-sussex-university-secure-sick-pay-win",
    "https://www.unitetheunion.org/news-events/news/2025/october/inverness-based-bear-scotland-workers-secure-union-recognition-and-wage-win",
    "https://www.unitetheunion.org/news-events/news/2025/october/gatwick-immigration-services-workers-strike-off-after-unite-secures-6-pay-deal",
    "https://www.unitetheunion.org/news-events/news/2025/october/unite-secures-significant-pay-victory-at-hsl-following-strike-action",
    "https://www.unitetheunion.org/news-events/news/2025/october/manchester-bee-network-bus-strikes-over-as-workers-win-excellent-pay-deal",
    "https://www.unitetheunion.org/news-events/news/2025/october/thousands-of-easyjet-workers-secure-bumper-pay-deal",
    "https://www.unitetheunion.org/news-events/news/2025/october/bournemouth-airport-strike-called-off-as-workers-given-improved-offer",
    "https://www.unitetheunion.org/news-events/news/2025/october/leicester-citybus-strikes-averted-as-drivers-get-bumper-pay-deal",
    "https://www.unitetheunion.org/news-events/news/2025/october/norwich-eaton-park-cafe-becomes-first-hospitality-venue-in-city-to-unionise",
    "https://www.unitetheunion.org/news-events/news/2025/october/wirral-council-biffa-bin-workers-in-unite-secure-5-pay-win",
    "https://www.unitetheunion.org/news-events/news/2025/october/birkenhead-chorley-and-preston-bus-strikes-off-after-inflation-busting-pay-victory",
    "https://www.unitetheunion.org/news-events/news/2025/october/first-manchester-strikes-called-off-after-exceptional-pay-deal-won",
    "https://www.unitetheunion.org/news-events/news/2025/october/collins-aerospace-workers-vote-to-accept-10-per-cent-pay-deal-and-end-pay-dispute",
    "https://www.unitetheunion.org/news-events/news/2025/october/bristol-bus-drivers-at-first-west-of-england-win-improved-pay-offer",
    "https://www.unitetheunion.org/news-events/news/2025/october/sussex-bus-strikes-in-brighton-and-crawley-off-as-workers-win-new-pay-award",
    "https://www.unitetheunion.org/news-events/news/2025/september/aw-crewing-strike-off-in-falmouth-as-workers-accept-improved-pay-deal",
    "https://www.unitetheunion.org/news-events/news/2025/september/strike-by-px-limited-at-sellafield-off-as-workers-accept-new-pay-deal",
    "https://www.unitetheunion.org/news-events/news/2025/september/birkenhead-chorley-and-preston-stagecoach-strikes-suspended-after-improved-pay-offer",
    "https://www.unitetheunion.org/news-events/news/2025/september/linamar-workforce-votes-to-accept-improved-pay-deal",
    "https://www.unitetheunion.org/news-events/news/2025/september/airbus-strike-action-off-after-new-deal-agreed",
    "https://www.unitetheunion.org/news-events/news/2025/september/edinburgh-airport-workers-back-new-pay-deal-averting-strikes",
    "https://www.unitetheunion.org/news-events/news/2025/september/arriva-bus-strikes-off-as-unite-wins-members-new-pay-deal",
    "https://www.unitetheunion.org/news-events/news/2025/september/unite-delivers-wage-win-for-cnooc-offshore-workers",
    "https://www.unitetheunion.org/news-events/news/2025/september/tarmac-derbyshire-strike-averted-as-workers-accept-improved-pay-offer",
    "https://www.unitetheunion.org/news-events/news/2025/september/leeds-housing-support-charity-gipsil-signs-unite-recognition-agreement",
    "https://www.unitetheunion.org/news-events/news/2025/september/unite-delivers-sweet-pay-deal-for-tunnock-s-factory-workers",
    "https://www.unitetheunion.org/news-events/news/2025/september/lincoln-siemens-energy-workers-celebrate-unite-pay-win-after-strike-vote",
    "https://www.unitetheunion.org/news-events/news/2025/august/cardiff-bus-strike-off-as-unite-members-accept-new-deal-on-pay-and-conditions",
    "https://www.unitetheunion.org/news-events/news/2025/august/ellesmere-port-electrical-oil-services-strikes-off-after-unite-secures-pay-win",
    "https://www.unitetheunion.org/news-events/news/2025/august/stagecoach-north-east-strikes-off-after-workers-accept-improved-pay-offer",
    "https://www.unitetheunion.org/news-events/news/2025/august/hundreds-of-plymouth-princess-yachts-workers-celebrate-huge-pay-win",
    "https://www.unitetheunion.org/news-events/news/2025/august/govan-village-hotel-strike-achieves-pay-and-conditions-win-for-workers",
    "https://www.unitetheunion.org/news-events/news/2025/august/gatwick-icts-baggage-screening-strikes-off-after-7-rise",
    "https://www.unitetheunion.org/news-events/news/2025/august/unite-secures-recognition-for-members-at-lineage-in-peterborough",
    "https://www.unitetheunion.org/news-events/news/2025/august/liverpool-university-staff-halt-strike-action-after-hybrid-working-win",
    "https://www.unitetheunion.org/news-events/news/2025/august/unite-craft-workers-back-cosla-pay-deal",
    "https://www.unitetheunion.org/news-events/news/2025/august/knottingley-lockwood-haulage-strikes-off-after-recognition-agreed",
    "https://www.unitetheunion.org/news-events/news/2025/august/glasgow-airport-summer-strike-action-averted-as-unite-delivers-major-pay-win",
    "https://www.unitetheunion.org/news-events/news/2025/july/unite-delivers-menzies-aviation-pay-deal-for-300-edinburgh-airport-workers",
    "https://www.unitetheunion.org/news-events/news/2025/july/unite-members-fly-high-with-pay-deals-at-aberdeen-airport",
    "https://www.unitetheunion.org/news-events/news/2025/july/unite-hails-latest-offshore-medics-recognition-agreement",
    "https://www.unitetheunion.org/news-events/news/2025/july/encirc-workers-in-bristol-secure-pay-rise-as-wine-bottle-shortage-averted",
    "https://www.unitetheunion.org/news-events/news/2025/july/victory-for-workers-in-long-running-oscar-mayer-dispute",
    "https://www.unitetheunion.org/news-events/news/2025/july/scottish-water-workers-celebrate-pay-victory",
    "https://www.unitetheunion.org/news-events/news/2025/july/unite-wins-recognition-deal-for-warehouse-workers-at-culina-logistics-in-tilbury-port",
    "https://www.unitetheunion.org/news-events/news/2025/july/thousands-of-electricians-benefit-from-14-pay-rise-secured-by-unite",
    "https://www.unitetheunion.org/news-events/news/2025/july/shell-s-offshore-medics-secure-pay-deal",
    "https://www.unitetheunion.org/news-events/news/2025/july/glasgow-subway-strike-action-ends-in-time-for-trnsmt-festival",
    "https://www.unitetheunion.org/news-events/news/2025/july/wincanton-strikes-called-off-as-unite-members-win-pay-victory",
    "https://www.unitetheunion.org/news-events/news/2025/june/heathrow-passenger-assistance-strikes-end-with-huge-125-pay-victory",
    "https://www.unitetheunion.org/news-events/news/2025/june/unite-delivers-pay-win-for-amcor-workers-in-ayrshire",
    "https://www.unitetheunion.org/news-events/news/2025/june/unite-hails-victory-over-pay-and-pensions-at-veolia-waste-plant-in-cheshire",
    "https://www.unitetheunion.org/news-events/news/2025/june/stagecoach-west-scotland-strikes-over-as-drivers-accept-new-pay-offer",
    "https://www.unitetheunion.org/news-events/news/2025/june/totalenergies-offshore-workers-win-boost-to-jobs-pay-and-conditions",
    "https://www.unitetheunion.org/news-events/news/2025/june/guys-and-st-thomas-cardiac-theatre-nurses-win-their-dispute",
    "https://www.unitetheunion.org/news-events/news/2025/june/gatwick-refuellers-strike-ends-after-unite-secures-pay-deal",
    "https://www.unitetheunion.org/news-events/news/2025/june/victory-for-gatwick-workers-as-pensions-problem-is-solved",
    "https://www.unitetheunion.org/news-events/news/2025/june/long-running-knowsley-livv-housing-strikes-end-with-fantastic-pay-victory",
    "https://www.unitetheunion.org/news-events/news/2025/may/unite-secures-double-digit-increase-in-pay-for-icts-workers-at-glasgow-airport",
    "https://www.unitetheunion.org/news-events/news/2025/may/unite-secures-wage-win-for-brake-brothers-workers-in-motherwell",
    "https://www.unitetheunion.org/news-events/news/2025/may/unite-secures-wage-wins-for-glasgow-airport-workers",
    "https://www.unitetheunion.org/news-events/news/2025/may/john-crane-strikes-in-slough-over-after-unite-members-accept-new-pay-deal",
    "https://www.unitetheunion.org/news-events/news/2025/may/north-air-tanker-driving-wage-wins-across-scottish-airports",
    "https://www.unitetheunion.org/news-events/news/2025/may/unite-extends-recognition-agreement-for-key-social-care-workers-across-scotland",
    "https://www.unitetheunion.org/news-events/news/2025/may/nhs-scotland-8-per-cent-pay-offer-over-two-years-accepted-by-unite-members",
    "https://www.unitetheunion.org/news-events/news/2025/may/scotrail-workers-accept-two-year-pay-offer",
    "https://www.unitetheunion.org/news-events/news/2025/may/wage-win-for-prestwick-airport-workers",
    "https://www.unitetheunion.org/news-events/news/2025/may/unite-delivers-wage-win-for-east-kilbride-based-ethigen-drivers",
    "https://www.unitetheunion.org/news-events/news/2025/may/first-bus-engineers-across-greater-glasgow-secure-bumper-pay-deal",
    "https://www.unitetheunion.org/news-events/news/2025/may/unite-secures-recognition-agreement-for-sodexo-workers-at-sullom-voe-terminal",
    "https://www.unitetheunion.org/news-events/news/2025/may/bus-strikes-in-telford-averted-after-unite-members-vote-to-accept-an-improved-pay-deal",
    "https://www.unitetheunion.org/news-events/news/2025/may/unite-delivers-pay-deal-for-east-kilbride-based-merson-signs",
    "https://www.unitetheunion.org/news-events/news/2025/april/pay-victory-for-unite-members-at-east-midlands-airport",
    "https://www.unitetheunion.org/news-events/news/2025/april/unite-secures-edinburgh-airport-pay-deal-for-hundreds-of-workers",
    "https://www.unitetheunion.org/news-events/news/2025/march/pay-victory-for-unite-members-at-first-bus-in-hampshire",
    "https://www.unitetheunion.org/news-events/news/2025/march/unite-members-celebrate-landmark-six-figure-pay-deal-with-american-airlines",
    "https://www.unitetheunion.org/news-events/news/2025/march/unite-member-wins-employment-tribunal-against-nhs-employer-for-detrimental-treatment",
    "https://www.unitetheunion.org/news-events/news/2025/march/birmingham-bmw-strikes-off-after-unite-secures-improved-pay-deal",
    "https://www.unitetheunion.org/news-events/news/2025/february/bolton-toby-carvery-workers-in-groundbreaking-campaign-for-union-recognition",
    "https://www.unitetheunion.org/news-events/news/2025/february/huddersfield-first-bus-strikes-off-after-unite-secures-pay-win-worth-nearly-16",
    "https://www.unitetheunion.org/news-events/news/2025/february/drax-canteen-workers-celebrate-another-inflation-busting-pay-rise",
    "https://www.unitetheunion.org/news-events/news/2025/february/battersea-power-station-celebrations-over-12-year-construction-project-involving-thousands-without-single-serious-accident",
    "https://www.unitetheunion.org/news-events/news/2025/february/unite-wins-significant-pay-award-for-british-airways-staff",
    "https://www.unitetheunion.org/news-events/news/2025/february/unite-wins-recognition-agreement-with-siemens-mobility-for-lincoln-workers",
    "https://www.unitetheunion.org/news-events/news/2025/january/huddersfield-first-bus-strikes-suspended-following-improved-pay-offer",
    "https://www.unitetheunion.org/news-events/news/2025/january/unite-delivers-new-recognition-agreement-for-advocacy-service-workers-in-aberdeen",
    "https://www.unitetheunion.org/news-events/news/2025/january/unite-delivers-recognition-agreement-for-security-workers-at-sullom-voe-terminal",
    "https://www.unitetheunion.org/news-events/news/2025/january/gloucestershire-stagecoach-strike-threat-ends-after-unite-secures-11-rise",
    "https://www.unitetheunion.org/news-events/news/2025/january/altrad-sellafield-strikes-off-as-workers-celebrate-huge-pay-win",
    "https://www.unitetheunion.org/news-events/news/2025/january/100-north-air-workers-secure-boost-to-jobs-pay-and-conditions-across-scottish-airports",
]


def submit_url(url: str, index: int, total: int) -> bool:
    """
    Submit a URL to the submission endpoint.

    Args:
        url: The URL to submit
        index: Current index (1-based)
        total: Total number of URLs

    Returns:
        True if successful, False otherwise
    """
    print(f"\n[{index}/{total}] Submitting: {url}")

    try:
        response = requests.post(
            SUBMISSION_ENDPOINT,
            json={"url": url},
            headers={"Content-Type": "application/json"},
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(
                    f"✅ Success: {data.get('message', 'Submitted successfully')}")
                return True
            else:
                print(f"❌ Failed: {data.get('message', 'Unknown error')}")
                return False
        elif response.status_code == 400:
            error_detail = response.json().get("detail", "Bad request")
            print(f"⚠️  Already submitted or error: {error_detail}")
            return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print(f"⏱️  Timeout after 60 seconds")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error - is the server running at {BASE_URL}?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main function to submit all URLs."""
    total_urls = len(URLS)
    successful = 0
    failed = 0

    print(
        f"🚀 Starting submission of {total_urls} URLs to {SUBMISSION_ENDPOINT}")
    print(f"⏱️  Delay between submissions: {DELAY_SECONDS} seconds")
    print("=" * 80)

    start_time = time.time()

    for i, url in enumerate(URLS, 1):
        success = submit_url(url, i, total_urls)

        if success:
            successful += 1
        else:
            failed += 1

        # Wait before next submission (except for the last one)
        if i < total_urls:
            print(
                f"⏳ Waiting {DELAY_SECONDS} seconds before next submission...")
            time.sleep(DELAY_SECONDS)

    elapsed_time = time.time() - start_time

    print("\n" + "=" * 80)
    print(f"✅ Completed in {elapsed_time:.1f} seconds")
    print(
        f"📊 Results: {successful} successful, {failed} failed out of {total_urls} total")
    print("=" * 80)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
