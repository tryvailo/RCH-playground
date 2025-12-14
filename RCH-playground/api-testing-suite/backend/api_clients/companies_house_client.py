"""
Companies House API Client
Enhanced with financial analysis, SIC code filtering, and monitoring capabilities
"""
import httpx
from typing import List, Dict, Optional
from datetime import datetime, date, timedelta


class CompaniesHouseAPIClient:
    """Companies House API Client with enhanced financial analysis"""
    
    # SIC codes for care homes
    CARE_HOME_SIC_CODES = [
        "87101",  # Residential nursing care activities
        "87300",  # Residential care activities for elderly/disabled
        "87200",  # Residential care activities for learning disabilities
        "87900",  # Other residential care activities
    ]
    
    def __init__(self, api_key: str):
        self.base_url = "https://api.company-information.service.gov.uk"
        self.api_key = api_key
        
        # Validate API key format (should be UUID format)
        if not api_key or len(api_key) < 10:
            raise ValueError("Invalid API key format")
        
        # Companies House uses HTTP Basic Auth: API key as username, empty password
        self.client = httpx.AsyncClient(
            timeout=30.0,
            auth=(api_key, "")  # HTTP Basic Auth
        )
    
    async def search_companies(
        self,
        query: str,
        items_per_page: int = 20
    ) -> List[Dict]:
        """Search for companies by name"""
        params = {
            "q": query,
            "items_per_page": items_per_page
        }
        
        try:
            response = await self.client.get(
                f"{self.base_url}/search/companies",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                error_msg = (
                    "Companies House API authentication failed (401 Unauthorized).\n"
                    "Please check:\n"
                    "1. API key is correct and active at https://developer.company-information.service.gov.uk/\n"
                    "2. IP address is registered in application settings\n"
                    "3. Application is in 'live' mode (not 'test')\n"
                    "4. You're using REST API key (not Streaming API key)"
                )
                raise Exception(error_msg)
            elif e.response.status_code == 429:
                raise Exception(f"Companies House API rate limit exceeded. Please wait before retrying.")
            else:
                error_detail = e.response.text[:200] if e.response.text else "No error details"
                raise Exception(f"Companies House API error (HTTP {e.response.status_code}): {error_detail}")
        except Exception as e:
            raise Exception(f"Companies House API error: {str(e)}")
    
    async def get_company_profile(self, company_number: str) -> Dict:
        """Get company profile"""
        try:
            response = await self.client.get(
                f"{self.base_url}/company/{company_number}"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                error_msg = (
                    "Companies House API authentication failed (401 Unauthorized).\n"
                    "Please check:\n"
                    "1. API key is correct and active at https://developer.company-information.service.gov.uk/\n"
                    "2. IP address is registered in application settings\n"
                    "3. Application is in 'live' mode (not 'test')\n"
                    "4. You're using REST API key (not Streaming API key)"
                )
                raise Exception(error_msg)
            elif e.response.status_code == 404:
                raise Exception(f"Company {company_number} not found")
            else:
                error_detail = e.response.text[:200] if e.response.text else "No error details"
                raise Exception(f"Companies House API error (HTTP {e.response.status_code}): {error_detail}")
        except Exception as e:
            raise Exception(f"Companies House API error: {str(e)}")
    
    async def get_company_officers(self, company_number: str) -> List[Dict]:
        """Get list of directors/officers"""
        try:
            response = await self.client.get(
                f"{self.base_url}/company/{company_number}/officers"
            )
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                error_msg = (
                    "Companies House API authentication failed (401 Unauthorized).\n"
                    "Please check:\n"
                    "1. API key is correct and active at https://developer.company-information.service.gov.uk/\n"
                    "2. IP address is registered in application settings\n"
                    "3. Application is in 'live' mode (not 'test')\n"
                    "4. You're using REST API key (not Streaming API key)"
                )
                raise Exception(error_msg)
            else:
                error_detail = e.response.text[:200] if e.response.text else "No error details"
                raise Exception(f"Companies House API error (HTTP {e.response.status_code}): {error_detail}")
        except Exception as e:
            raise Exception(f"Companies House API error: {str(e)}")
    
    async def get_charges(self, company_number: str) -> List[Dict]:
        """Get charges (mortgages, debts)"""
        try:
            response = await self.client.get(
                f"{self.base_url}/company/{company_number}/charges"
            )
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                error_msg = (
                    "Companies House API authentication failed (401 Unauthorized).\n"
                    "Please check:\n"
                    "1. API key is correct and active at https://developer.company-information.service.gov.uk/\n"
                    "2. IP address is registered in application settings\n"
                    "3. Application is in 'live' mode (not 'test')\n"
                    "4. You're using REST API key (not Streaming API key)"
                )
                raise Exception(error_msg)
            else:
                error_detail = e.response.text[:200] if e.response.text else "No error details"
                raise Exception(f"Companies House API error (HTTP {e.response.status_code}): {error_detail}")
        except Exception as e:
            raise Exception(f"Companies House API error: {str(e)}")
    
    async def get_filing_history(self, company_number: str, items_per_page: int = 10) -> List[Dict]:
        """Get filing history (documents submitted to Companies House)"""
        try:
            response = await self.client.get(
                f"{self.base_url}/company/{company_number}/filing-history",
                params={"items_per_page": items_per_page}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                error_msg = (
                    "Companies House API authentication failed (401 Unauthorized).\n"
                    "Please check:\n"
                    "1. API key is correct and active at https://developer.company-information.service.gov.uk/\n"
                    "2. IP address is registered in application settings\n"
                    "3. Application is in 'live' mode (not 'test')\n"
                    "4. You're using REST API key (not Streaming API key)"
                )
                raise Exception(error_msg)
            elif e.response.status_code == 404:
                return []  # No filing history
            else:
                error_detail = e.response.text[:200] if e.response.text else "No error details"
                raise Exception(f"Companies House API error (HTTP {e.response.status_code}): {error_detail}")
        except Exception as e:
            raise Exception(f"Companies House API error: {str(e)}")
    
    async def get_insolvency(self, company_number: str) -> Dict:
        """Get insolvency information"""
        try:
            response = await self.client.get(
                f"{self.base_url}/company/{company_number}/insolvency"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                error_msg = (
                    "Companies House API authentication failed (401 Unauthorized).\n"
                    "Please check:\n"
                    "1. API key is correct and active at https://developer.company-information.service.gov.uk/\n"
                    "2. IP address is registered in application settings\n"
                    "3. Application is in 'live' mode (not 'test')\n"
                    "4. You're using REST API key (not Streaming API key)"
                )
                raise Exception(error_msg)
            elif e.response.status_code == 404:
                return {}  # No insolvency data
            else:
                error_detail = e.response.text[:200] if e.response.text else "No error details"
                raise Exception(f"Companies House API error (HTTP {e.response.status_code}): {error_detail}")
        except Exception as e:
            raise Exception(f"Companies House API error: {str(e)}")
    
    async def get_persons_with_significant_control(self, company_number: str) -> List[Dict]:
        """Get Persons with Significant Control (PSC) - ownership structure"""
        try:
            response = await self.client.get(
                f"{self.base_url}/company/{company_number}/persons-with-significant-control"
            )
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                error_msg = (
                    "Companies House API authentication failed (401 Unauthorized).\n"
                    "Please check:\n"
                    "1. API key is correct and active at https://developer.company-information.service.gov.uk/\n"
                    "2. IP address is registered in application settings\n"
                    "3. Application is in 'live' mode (not 'test')\n"
                    "4. You're using REST API key (not Streaming API key)"
                )
                raise Exception(error_msg)
            elif e.response.status_code == 404:
                return []  # No PSC data
            else:
                error_detail = e.response.text[:200] if e.response.text else "No error details"
                raise Exception(f"Companies House API error (HTTP {e.response.status_code}): {error_detail}")
        except Exception as e:
            raise Exception(f"Companies House API error: {str(e)}")
    
    async def search_care_homes(
        self,
        location: Optional[str] = None,
        items_per_page: int = 20
    ) -> List[Dict]:
        """
        Search for care homes by SIC codes
        
        Args:
            location: Optional location filter (e.g., "Birmingham")
            items_per_page: Number of results per page
            
        Returns:
            List of care home companies
        """
        results = []
        
        for sic_code in self.CARE_HOME_SIC_CODES:
            query = sic_code
            if location:
                query = f"{sic_code} {location}"
            
            companies = await self.search_companies(query, items_per_page)
            
            # Filter by SIC codes
            for company in companies:
                desc_ids = company.get("description_identifier", [])
                if any(code in self.CARE_HOME_SIC_CODES for code in desc_ids):
                    # Avoid duplicates
                    if not any(r.get("company_number") == company.get("company_number") for r in results):
                        results.append(company)
        
        return results
    
    async def find_company_by_name(
        self,
        company_name: str,
        prefer_care_home: bool = True
    ) -> Optional[str]:
        """
        Find company number by name
        
        Args:
            company_name: Company name to search
            prefer_care_home: Prefer companies with care home SIC codes
            
        Returns:
            Company number or None
        """
        companies = await self.search_companies(company_name, items_per_page=10)
        
        if not companies:
            return None
        
        # Priority: active status + care home SIC code
        if prefer_care_home:
            for company in companies:
                if company.get("company_status") == "active":
                    desc_ids = company.get("description_identifier", [])
                    if any(code in self.CARE_HOME_SIC_CODES for code in desc_ids):
                        return company.get("company_number")
        
        # Fallback: first active result
        for company in companies:
            if company.get("company_status") == "active":
                return company.get("company_number")
        
        # Fallback: any result
        return companies[0].get("company_number") if companies else None
    
    async def get_detailed_financial_metrics(self, company_number: str) -> Dict:
        """
        Get comprehensive financial metrics for a company
        
        Returns detailed metrics including:
        - Company age
        - Accounts status
        - Charges summary
        - Director stability
        - Filing history summary
        """
        profile = await self.get_company_profile(company_number)
        
        # Parse dates
        creation_date = None
        company_age_years = 0
        if profile.get("date_of_creation"):
            try:
                creation_date = datetime.strptime(profile["date_of_creation"], "%Y-%m-%d").date()
                company_age_years = (date.today() - creation_date).days / 365.25
            except:
                pass
        
        # Accounts analysis
        accounts = profile.get("accounts", {})
        accounts_overdue = accounts.get("overdue", False)
        last_accounts_date = None
        days_since_accounts = None
        next_accounts_due = None
        
        if accounts.get("last_accounts", {}).get("made_up_to"):
            try:
                last_accounts_date = datetime.strptime(
                    accounts["last_accounts"]["made_up_to"], "%Y-%m-%d"
                ).date()
                days_since_accounts = (date.today() - last_accounts_date).days
            except:
                pass
        
        if accounts.get("next_due"):
            try:
                next_accounts_due = datetime.strptime(accounts["next_due"], "%Y-%m-%d").date()
            except:
                pass
        
        # Charges analysis
        charges_data = {"outstanding": 0, "total": 0, "satisfied": 0}
        try:
            charges = await self.get_charges(company_number)
            charges_data["total"] = len(charges)
            charges_data["outstanding"] = len([c for c in charges if not c.get("satisfied_on")])
            charges_data["satisfied"] = len([c for c in charges if c.get("satisfied_on")])
        except:
            pass
        
        # Directors analysis
        directors_data = {"active": 0, "resigned_last_year": 0, "total": 0}
        try:
            officers = await self.get_company_officers(company_number)
            directors = [o for o in officers if o.get("officer_role") == "director"]
            directors_data["total"] = len(directors)
            directors_data["active"] = len([d for d in directors if not d.get("resigned_on")])
            
            # Count resignations in last year
            one_year_ago = date.today() - timedelta(days=365)
            for director in directors:
                if director.get("resigned_on"):
                    try:
                        resign_date = datetime.strptime(director["resigned_on"], "%Y-%m-%d").date()
                        if resign_date >= one_year_ago:
                            directors_data["resigned_last_year"] += 1
                    except:
                        pass
        except:
            pass
        
        # Filing history summary
        filing_summary = {"recent_filings": 0, "last_filing_date": None}
        try:
            filings = await self.get_filing_history(company_number, items_per_page=5)
            filing_summary["recent_filings"] = len(filings)
            if filings:
                try:
                    filing_summary["last_filing_date"] = filings[0].get("date")
                except:
                    pass
        except:
            pass
        
        return {
            "company_number": company_number,
            "company_name": profile.get("company_name", ""),
            "status": profile.get("company_status", ""),
            "incorporation_date": profile.get("date_of_creation"),
            "company_age_years": round(company_age_years, 1),
            "accounts": {
                "overdue": accounts_overdue,
                "last_accounts_date": str(last_accounts_date) if last_accounts_date else None,
                "days_since_accounts": days_since_accounts,
                "next_due": str(next_accounts_due) if next_accounts_due else None,
            },
            "charges": charges_data,
            "directors": directors_data,
            "insolvency_history": profile.get("has_insolvency_history", False),
            "sic_codes": profile.get("sic_codes", []),
            "filing_history": filing_summary,
        }
    
    async def calculate_financial_stability_score(self, company_number: str) -> Dict:
        """Calculate financial stability score (0-100, higher = better)"""
        profile = await self.get_company_profile(company_number)
        
        score = 100
        issues = []
        breakdown = []
        
        # Company status (critical)
        status = profile.get("company_status", "").lower()
        if status != "active":
            score = 0
            issues.append(f"Company status: {status}")
            breakdown.append(f"Company not active ({status}): -100 points")
            return {
                "company_name": profile.get("company_name", ""),
                "company_number": company_number,
                "score": 0,
                "risk_level": "CRITICAL",
                "risk_label": "🚨 CRITICAL",
                "risk_description": "Company is not active - do not recommend",
                "issues": issues,
                "company_status": profile.get("company_status", ""),
                "breakdown": breakdown
            }
        
        # Insolvency (critical)
        if profile.get("has_insolvency_history"):
            score = 0
            issues.append("Has insolvency history")
            breakdown.append("Insolvency history: -100 points (CRITICAL)")
            return {
                "company_name": profile.get("company_name", ""),
                "company_number": company_number,
                "score": 0,
                "risk_level": "CRITICAL",
                "risk_label": "🚨 CRITICAL",
                "risk_description": "Company has insolvency history - do not recommend",
                "issues": issues,
                "company_status": profile.get("company_status", ""),
                "breakdown": breakdown
            }
        
        # Accounts overdue (40 points)
        accounts = profile.get("accounts", {})
        if accounts.get("overdue"):
            score -= 40
            issues.append("Accounts filing overdue")
            breakdown.append("Accounts overdue: -40 points")
        else:
            breakdown.append("Accounts up to date: +0 points")
        
        # Days since last accounts (20 points)
        last_accounts = accounts.get("last_accounts", {})
        if last_accounts.get("made_up_to"):
            from datetime import datetime, date
            try:
                made_up_to = datetime.strptime(last_accounts["made_up_to"], "%Y-%m-%d").date()
                days_since = (date.today() - made_up_to).days
                if days_since > 730:  # 2 years
                    score -= 20
                    issues.append(f"Last accounts over 2 years ago ({days_since} days)")
                    breakdown.append(f"Last accounts {days_since} days ago: -20 points")
                elif days_since > 365:  # 1 year
                    score -= 10
                    breakdown.append(f"Last accounts {days_since} days ago: -10 points")
                else:
                    breakdown.append(f"Recent accounts ({days_since} days ago): +0 points")
            except:
                pass
        
        # Charges (25 points)
        try:
            charges = await self.get_charges(company_number)
            outstanding = [c for c in charges if not c.get("satisfied_on")]
            total_charges = len(charges)
            outstanding_count = len(outstanding)
            
            if outstanding_count >= 3:
                score -= 25
                issues.append(f"{outstanding_count} outstanding charges")
                breakdown.append(f"{outstanding_count} outstanding charges: -25 points")
            elif outstanding_count >= 1:
                score -= 15
                breakdown.append(f"{outstanding_count} outstanding charge(s): -15 points")
            else:
                breakdown.append("No outstanding charges: +0 points")
        except:
            breakdown.append("Charges data unavailable: +0 points")
        
        # Company age (20 points)
        date_of_creation = profile.get("date_of_creation")
        if date_of_creation:
            from datetime import datetime, date
            try:
                creation_date = datetime.strptime(date_of_creation, "%Y-%m-%d").date()
                age_years = (date.today() - creation_date).days / 365.25
                
                if age_years < 2:
                    score -= 20
                    issues.append(f"Young company ({age_years:.1f} years old)")
                    breakdown.append(f"Company age {age_years:.1f} years: -20 points")
                elif age_years < 5:
                    score -= 10
                    breakdown.append(f"Company age {age_years:.1f} years: -10 points")
                else:
                    breakdown.append(f"Established company ({age_years:.1f} years): +0 points")
            except:
                pass
        
        # Director stability (15 points)
        try:
            officers = await self.get_company_officers(company_number)
            active_officers = [o for o in officers if not o.get("resigned_on")]
            active_count = len(active_officers)
            
            if active_count == 0:
                score -= 15
                issues.append("No active directors")
                breakdown.append("No active directors: -15 points")
            elif active_count < 2:
                score -= 5
                breakdown.append(f"Only {active_count} active director(s): -5 points")
            else:
                breakdown.append(f"{active_count} active directors: +0 points")
        except:
            breakdown.append("Directors data unavailable: +0 points")
        
        final_score = max(0, score)
        
        # Determine risk level
        if final_score >= 90:
            risk_level = "MINIMAL"
            risk_label = "✅ MINIMAL"
            risk_description = "Excellent financial health"
        elif final_score >= 70:
            risk_level = "LOW"
            risk_label = "🟢 LOW"
            risk_description = "Minor concerns - generally safe"
        elif final_score >= 50:
            risk_level = "MEDIUM"
            risk_label = "🟡 MEDIUM"
            risk_description = "Some concerns - monitor carefully"
        elif final_score >= 30:
            risk_level = "HIGH"
            risk_label = "🔴 HIGH"
            risk_description = "Significant concerns - use caution"
        else:
            risk_level = "CRITICAL"
            risk_label = "🚨 CRITICAL"
            risk_description = "Do not recommend - severe financial distress"
        
        return {
            "company_name": profile.get("company_name", ""),
            "company_number": company_number,
            "score": final_score,
            "risk_level": risk_level,
            "risk_label": risk_label,
            "risk_description": risk_description,
            "issues": issues,
            "company_status": profile.get("company_status", ""),
            "breakdown": breakdown,
            "max_score": 100
        }
    
    async def compare_companies(self, company_numbers: List[str]) -> List[Dict]:
        """
        Compare multiple companies by their financial metrics
        
        Args:
            company_numbers: List of company numbers to compare
            
        Returns:
            List of financial metrics sorted by risk (safest first)
        """
        results = []
        
        for company_number in company_numbers:
            try:
                metrics = await self.get_detailed_financial_metrics(company_number)
                stability = await self.calculate_financial_stability_score(company_number)
                
                # Merge metrics with stability score
                metrics["financial_stability"] = stability
                results.append(metrics)
            except Exception as e:
                # Skip companies that fail to load
                print(f"Error loading company {company_number}: {e}")
                continue
        
        # Sort by risk score (lowest = safest)
        results.sort(key=lambda x: x.get("financial_stability", {}).get("score", 100), reverse=True)
        
        return results
    
    async def detect_changes(
        self,
        company_number: str,
        previous_state: Optional[Dict] = None
    ) -> Dict:
        """
        Detect changes in company financial status
        
        Args:
            company_number: Company number to check
            previous_state: Previous state for comparison (optional)
            
        Returns:
            Dictionary with detected changes and alerts
        """
        current_metrics = await self.get_detailed_financial_metrics(company_number)
        current_stability = await self.calculate_financial_stability_score(company_number)
        
        alerts = []
        changes = {}
        
        if previous_state:
            # Compare status
            if current_metrics["status"] != previous_state.get("status"):
                alerts.append({
                    "type": "status_change",
                    "severity": "critical",
                    "message": f"Status changed: {previous_state.get('status')} → {current_metrics['status']}",
                    "date": datetime.now().isoformat()
                })
                changes["status"] = {
                    "previous": previous_state.get("status"),
                    "current": current_metrics["status"]
                }
            
            # Compare accounts overdue
            if current_metrics["accounts"]["overdue"] and not previous_state.get("accounts", {}).get("overdue"):
                alerts.append({
                    "type": "accounts_overdue",
                    "severity": "high",
                    "message": "Accounts are now overdue",
                    "date": datetime.now().isoformat()
                })
                changes["accounts_overdue"] = True
            
            # Compare charges
            prev_outstanding = previous_state.get("charges", {}).get("outstanding", 0)
            curr_outstanding = current_metrics["charges"]["outstanding"]
            
            if curr_outstanding > prev_outstanding:
                new_charges = curr_outstanding - prev_outstanding
                alerts.append({
                    "type": "new_charges",
                    "severity": "medium",
                    "message": f"{new_charges} new charge(s) filed",
                    "date": datetime.now().isoformat()
                })
                changes["new_charges"] = new_charges
            
            # Compare directors
            prev_active = previous_state.get("directors", {}).get("active", 0)
            curr_active = current_metrics["directors"]["active"]
            
            if curr_active < prev_active:
                resigned = prev_active - curr_active
                alerts.append({
                    "type": "director_resignation",
                    "severity": "medium",
                    "message": f"{resigned} director(s) resigned",
                    "date": datetime.now().isoformat()
                })
                changes["directors_resigned"] = resigned
            
            # Compare risk level
            prev_risk = previous_state.get("financial_stability", {}).get("risk_level", "")
            curr_risk = current_stability.get("risk_level", "")
            
            if prev_risk != curr_risk:
                # Risk increased
                risk_levels = ["MINIMAL", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
                prev_idx = risk_levels.index(prev_risk) if prev_risk in risk_levels else -1
                curr_idx = risk_levels.index(curr_risk) if curr_risk in risk_levels else -1
                
                if curr_idx > prev_idx:
                    alerts.append({
                        "type": "risk_increase",
                        "severity": "high",
                        "message": f"Risk level increased: {prev_risk} → {curr_risk}",
                        "date": datetime.now().isoformat()
                    })
                    changes["risk_level"] = {
                        "previous": prev_risk,
                        "current": curr_risk
                    }
        else:
            # No previous state - return current state as baseline
            changes["baseline"] = True
        
        return {
            "company_number": company_number,
            "company_name": current_metrics["company_name"],
            "current_metrics": current_metrics,
            "current_stability": current_stability,
            "changes": changes,
            "alerts": alerts,
            "checked_at": datetime.now().isoformat()
        }
    
    def interpret_company_profile(self, profile: Dict) -> Dict:
        """
        Interpret company profile data for risk signals
        
        Returns risk_signals dict with weights
        """
        risk_signals = {
            'signals': [],
            'total_weight': 0.0
        }
        
        # CRITICAL: Accounts overdue
        accounts = profile.get('accounts', {})
        if accounts.get('overdue'):
            risk_signals['signals'].append({
                'type': 'ACCOUNTS_OVERDUE',
                'weight': 0.4,
                'severity': 'HIGH',
                'message': 'Company has overdue accounts filing - indicates financial stress or poor governance',
                'timeline': '12-18 months warning'
            })
            risk_signals['total_weight'] += 0.4
        
        # CRITICAL: Insolvency history
        if profile.get('has_insolvency_history'):
            risk_signals['signals'].append({
                'type': 'INSOLVENCY_HISTORY',
                'weight': 0.8,
                'severity': 'CRITICAL',
                'message': 'Company has past insolvency - significantly higher failure risk',
                'timeline': '6-12 months warning'
            })
            risk_signals['total_weight'] += 0.8
        
        # Company in distress status
        distress_statuses = ['administration', 'liquidation', 'receivership']
        company_status = profile.get('company_status', '').lower()
        if company_status in distress_statuses:
            risk_signals['signals'].append({
                'type': 'DISTRESS_STATUS',
                'weight': 1.0,
                'severity': 'CRITICAL',
                'message': f"Company in {company_status} - IMMEDIATE RISK",
                'timeline': '0-3 months'
            })
            risk_signals['total_weight'] += 1.0
        
        # Has secured charges (debt)
        if profile.get('has_charges'):
            risk_signals['signals'].append({
                'type': 'HAS_CHARGES',
                'weight': 0.3,
                'severity': 'MEDIUM',
                'message': 'Company has secured debt - monitor charge details',
                'timeline': '6-12 months context'
            })
            risk_signals['total_weight'] += 0.3
        
        return risk_signals
    
    def analyze_filing_patterns(self, filings: List[Dict], profile: Dict) -> Dict:
        """
        Analyze filing history for distress patterns
        
        CRITICAL PATTERNS:
        1. Late account filings (gap between action_date and date)
        2. Multiple charges registered in short period
        3. High frequency of officer changes
        4. Paper filings (old-school, may indicate IT/resource issues)
        """
        patterns = {
            'late_filings_count': 0,
            'charges_last_12mo': 0,
            'officer_changes_last_12mo': 0,
            'risk_signals': []
        }
        
        now = datetime.now()
        twelve_months_ago = now - timedelta(days=365)
        
        # Check for late account filings
        account_filings = [f for f in filings if f.get('category') == 'accounts']
        for filing in account_filings[:3]:  # Check last 3 account filings
            action_date_str = filing.get('action_date')
            filed_date_str = filing.get('date')
            
            if action_date_str and filed_date_str:
                try:
                    action_date = datetime.fromisoformat(action_date_str.replace('Z', '+00:00'))
                    filed_date = datetime.fromisoformat(filed_date_str.replace('Z', '+00:00'))
                    days_late = (filed_date - action_date).days
                    
                    # Accounts should be filed within 9 months for private companies
                    if days_late > 270:
                        patterns['late_filings_count'] += 1
                        patterns['risk_signals'].append({
                            'type': 'LATE_FILING',
                            'weight': 0.2,
                            'severity': 'MEDIUM',
                            'message': f'Accounts filed {days_late} days late (period ending {action_date_str})',
                            'timeline': '12-18 months warning'
                        })
                except Exception:
                    pass
        
        # Count charges in last 12 months
        recent_charges = []
        for filing in filings:
            if filing.get('category') == 'charge':
                filing_date_str = filing.get('date')
                if filing_date_str:
                    try:
                        filing_date = datetime.fromisoformat(filing_date_str.replace('Z', '+00:00'))
                        if filing_date > twelve_months_ago:
                            recent_charges.append(filing)
                    except Exception:
                        pass
        
        patterns['charges_last_12mo'] = len(recent_charges)
        
        if len(recent_charges) >= 2:
            patterns['risk_signals'].append({
                'type': 'MULTIPLE_CHARGES',
                'weight': 0.5,
                'severity': 'HIGH',
                'message': f'{len(recent_charges)} new charges registered in last 12 months - raising debt rapidly',
                'timeline': '6-12 months warning'
            })
        
        # Count officer changes
        officer_changes = []
        for filing in filings:
            filing_type = filing.get('type', '').lower()
            filing_date_str = filing.get('date')
            if 'officer' in filing_type or 'director' in filing_type:
                if filing_date_str:
                    try:
                        filing_date = datetime.fromisoformat(filing_date_str.replace('Z', '+00:00'))
                        if filing_date > twelve_months_ago:
                            officer_changes.append(filing)
                    except Exception:
                        pass
        
        patterns['officer_changes_last_12mo'] = len(officer_changes)
        
        if len(officer_changes) >= 4:
            patterns['risk_signals'].append({
                'type': 'HIGH_OFFICER_TURNOVER',
                'weight': 0.8,
                'severity': 'HIGH',
                'message': f'{len(officer_changes)} officer changes in last 12 months - severe instability',
                'timeline': '6-18 months warning'
            })
        
        return patterns
    
    def analyze_debt_structure(self, charges: List[Dict]) -> Dict:
        """
        Analyze debt structure for distress signals
        
        CRITICAL RED FLAGS:
        1. Related party charges (especially offshore)
        2. Multiple recent charges (raising emergency debt)
        3. Charges over ALL property (no unencumbered assets)
        4. Sale-and-leaseback indicators
        """
        analysis = {
            'total_outstanding': 0,
            'related_party_charges': [],
            'covers_all_property': False,
            'risk_signals': []
        }
        
        outstanding_charges = [c for c in charges if c.get('status') == 'outstanding']
        analysis['total_outstanding'] = len(outstanding_charges)
        
        # Check for related party charges (offshore indicators)
        offshore_keywords = ['limited', 'holdings', 'jersey', 'cayman', 'guernsey', 'bvi', 'isle of man']
        for charge in outstanding_charges:
            persons_entitled = charge.get('persons_entitled', [])
            if isinstance(persons_entitled, list):
                for person in persons_entitled:
                    person_name = person.get('name', '') if isinstance(person, dict) else str(person)
                    person_lower = person_name.lower()
                    if any(keyword in person_lower for keyword in offshore_keywords):
                        if 'care' not in person_lower:  # Avoid false positives
                            analysis['related_party_charges'].append({
                                'person': person_name,
                                'created': charge.get('created_on'),
                                'particulars': str(charge.get('particulars', {}).get('description', ''))[:200] if isinstance(charge.get('particulars'), dict) else str(charge.get('particulars', ''))[:200]
                            })
        
        if len(analysis['related_party_charges']) > 0:
            analysis['risk_signals'].append({
                'type': 'OFFSHORE_RELATED_DEBT',
                'weight': 0.6,
                'severity': 'HIGH',
                'message': f'{len(analysis["related_party_charges"])} charges to potential related parties/offshore entities',
                'timeline': '12-24 months context',
                'detail': 'Private equity ownership often extracts profits through high-interest loans to offshore companies'
            })
        
        # Check if all property is covered
        for charge in outstanding_charges:
            secured_details = charge.get('secured_details', {})
            if isinstance(secured_details, dict):
                description = secured_details.get('description', '').lower()
                if 'all' in description and ('property' in description or 'undertaking' in description):
                    analysis['covers_all_property'] = True
                    break
        
        if analysis['covers_all_property']:
            analysis['risk_signals'].append({
                'type': 'ALL_PROPERTY_CHARGED',
                'weight': 0.5,
                'severity': 'HIGH',
                'message': 'All company property is charged - no unencumbered assets remain',
                'timeline': '6-12 months warning'
            })
        
        # Sale-and-leaseback detection
        sale_leaseback_keywords = ['sale and leaseback', 'property rental', 'lease agreement']
        for charge in outstanding_charges:
            particulars = charge.get('particulars', {})
            if isinstance(particulars, dict):
                description = particulars.get('description', '')
            else:
                description = str(particulars)
            
            description_lower = description.lower()
            if any(keyword in description_lower for keyword in sale_leaseback_keywords):
                analysis['risk_signals'].append({
                    'type': 'SALE_LEASEBACK',
                    'weight': 0.7,
                    'severity': 'HIGH',
                    'message': 'Sale-and-leaseback detected - creates fixed rent obligations',
                    'timeline': '12-36 months context',
                    'detail': 'Southern Cross collapsed due to £240M annual rent from sale-leaseback'
                })
                break
        
        return analysis
    
    def analyze_director_turnover(self, officers: List[Dict], filing_history: List[Dict]) -> Dict:
        """
        Analyze director changes for instability signals
        
        CRITICAL: Care sector median turnover is 52.1%, but director-level
        turnover is much more concerning
        """
        analysis = {
            'active_directors': 0,
            'resignations_last_18mo': 0,
            'mass_resignation_event': False,
            'risk_signals': []
        }
        
        now = datetime.now()
        eighteen_months_ago = now - timedelta(days=547)
        
        # Count active directors
        active = [o for o in officers if not o.get('resigned_on')]
        analysis['active_directors'] = len(active)
        
        # Count recent resignations
        recent_resignations = []
        for officer in officers:
            resigned_on_str = officer.get('resigned_on')
            if resigned_on_str:
                try:
                    resign_date = datetime.fromisoformat(resigned_on_str.replace('Z', '+00:00'))
                    if resign_date > eighteen_months_ago:
                        recent_resignations.append(officer)
                except Exception:
                    pass
        
        analysis['resignations_last_18mo'] = len(recent_resignations)
        
        # Detect mass resignation (3+ directors within 90 days)
        if len(recent_resignations) >= 3:
            resignation_dates = []
            for officer in recent_resignations:
                try:
                    resign_date = datetime.fromisoformat(officer['resigned_on'].replace('Z', '+00:00'))
                    resignation_dates.append(resign_date)
                except Exception:
                    pass
            
            resignation_dates.sort()
            
            for i in range(len(resignation_dates) - 2):
                date_span = (resignation_dates[i+2] - resignation_dates[i]).days
                if date_span <= 90:
                    analysis['mass_resignation_event'] = True
                    analysis['risk_signals'].append({
                        'type': 'MASS_RESIGNATION',
                        'weight': 1.0,
                        'severity': 'CRITICAL',
                        'message': f'{len(recent_resignations)} directors resigned within 90 days',
                        'timeline': '3-6 months warning',
                        'detail': 'Mass resignations indicate severe internal problems or imminent failure'
                    })
                    break
        
        # High turnover signal
        if analysis['resignations_last_18mo'] >= 4:
            analysis['risk_signals'].append({
                'type': 'HIGH_DIRECTOR_TURNOVER',
                'weight': 0.8,
                'severity': 'HIGH',
                'message': f'{analysis["resignations_last_18mo"]} director changes in 18 months',
                'timeline': '6-18 months warning'
            })
        
        # Low active directors (should have 2+ for care homes)
        if analysis['active_directors'] < 2:
            analysis['risk_signals'].append({
                'type': 'LOW_DIRECTOR_COUNT',
                'weight': 0.4,
                'severity': 'MEDIUM',
                'message': f'Only {analysis["active_directors"]} active director(s) - governance risk',
                'timeline': '6-12 months context'
            })
        
        return analysis
    
    def analyze_ownership_structure(self, pscs: List[Dict]) -> Dict:
        """
        Analyze ownership for private equity and offshore signals
        
        CRITICAL: Private equity homes have £35,072 debt per bed vs 
        £21,069 for not-for-profit. PE ownership = higher risk.
        """
        analysis = {
            'private_equity_indicators': [],
            'offshore_entities': [],
            'recent_ownership_changes': [],
            'risk_signals': []
        }
        
        # Private equity keywords
        pe_keywords = ['capital', 'partners', 'equity', 'investment', 'fund', 'holdings']
        
        # Offshore jurisdictions
        offshore_jurisdictions = [
            'jersey', 'guernsey', 'cayman', 'bvi', 'british virgin islands',
            'isle of man', 'bermuda', 'luxembourg', 'malta', 'gibraltar',
            'liechtenstein', 'monaco', 'bahamas', 'seychelles'
        ]
        
        active_pscs = [p for p in pscs if not p.get('ceased_on')]
        
        for psc in active_pscs:
            name = psc.get('name', '')
            name_lower = name.lower()
            
            # Detect private equity
            if any(keyword in name_lower for keyword in pe_keywords):
                analysis['private_equity_indicators'].append({
                    'name': name,
                    'kind': psc.get('kind'),
                    'notified_on': psc.get('notified_on')
                })
            
            # Detect offshore corporate entities
            if psc.get('kind') == 'corporate-entity':
                identification = psc.get('identification', {})
                if isinstance(identification, dict):
                    jurisdiction = identification.get('legal_authority', '').lower()
                    country = identification.get('country_registered', '').lower()
                else:
                    jurisdiction = ''
                    country = ''
                
                address = psc.get('address', {})
                if isinstance(address, dict):
                    address_country = address.get('country', '').lower()
                else:
                    address_country = ''
                
                if any(off in jurisdiction or off in country or off in address_country 
                       for off in offshore_jurisdictions):
                    analysis['offshore_entities'].append({
                        'name': name,
                        'jurisdiction': jurisdiction or country or address_country,
                        'notified_on': psc.get('notified_on')
                    })
        
        # Check for recent ownership changes (last 24 months)
        now = datetime.now()
        two_years_ago = now - timedelta(days=730)
        
        recent_changes = []
        for psc in pscs:
            notified_on_str = psc.get('notified_on')
            if notified_on_str:
                try:
                    notified_on = datetime.fromisoformat(notified_on_str.replace('Z', '+00:00'))
                    if notified_on > two_years_ago:
                        recent_changes.append(psc)
                except Exception:
                    pass
        
        analysis['recent_ownership_changes'] = len(recent_changes)
        
        # Generate risk signals
        if len(analysis['private_equity_indicators']) > 0:
            analysis['risk_signals'].append({
                'type': 'PRIVATE_EQUITY_OWNERSHIP',
                'weight': 0.5,
                'severity': 'MEDIUM',
                'message': f'Private equity ownership detected: {analysis["private_equity_indicators"][0]["name"]}',
                'timeline': '12-36 months context',
                'detail': 'PE homes have £35,072 debt per bed vs £21,069 non-profit average. Pay £102/bed/week interest vs £19.'
            })
        
        if len(analysis['offshore_entities']) > 0:
            analysis['risk_signals'].append({
                'type': 'OFFSHORE_OWNERSHIP',
                'weight': 0.6,
                'severity': 'HIGH',
                'message': f'{len(analysis["offshore_entities"])} offshore entities detected',
                'timeline': '12-24 months context',
                'detail': '59.2% of debt in largest providers flows to offshore related companies. Profit extraction risk.'
            })
        
        if analysis['recent_ownership_changes'] >= 2:
            analysis['risk_signals'].append({
                'type': 'OWNERSHIP_CHURN',
                'weight': 0.5,
                'severity': 'MEDIUM',
                'message': f'{analysis["recent_ownership_changes"]} ownership changes in last 24 months',
                'timeline': '6-12 months warning',
                'detail': 'Frequent ownership changes indicate instability or financial distress'
            })
        
        return analysis
    
    def calculate_composite_risk_score(
        self,
        profile_signals: Dict,
        filing_signals: Dict,
        charge_signals: Dict,
        officer_signals: Dict,
        psc_signals: Dict
    ) -> Dict:
        """
        Calculate composite risk score from all data sources
        
        SCORING SYSTEM:
        - Aggregate weights from all signals in 90-day window
        - Total ≥2.0 = CRITICAL (90-100 score)
        - Total ≥1.0 = HIGH (70-89 score)
        - Total ≥0.5 = MEDIUM (40-69 score)
        - Total <0.5 = LOW (0-39 score)
        """
        # Collect all signals
        all_signals = []
        
        for source in [profile_signals, filing_signals, charge_signals, officer_signals, psc_signals]:
            for signal in source.get('risk_signals', []):
                all_signals.append(signal)
        
        # Calculate total weight
        total_weight = sum(signal.get('weight', 0) for signal in all_signals)
        
        # Determine risk level
        if total_weight >= 2.0:
            risk_level = 'CRITICAL'
            risk_score = min(90 + int(total_weight * 5), 100)
        elif total_weight >= 1.0:
            risk_level = 'HIGH'
            risk_score = 70 + int((total_weight - 1.0) * 20)
        elif total_weight >= 0.5:
            risk_level = 'MEDIUM'
            risk_score = 40 + int((total_weight - 0.5) * 60)
        else:
            risk_level = 'LOW'
            risk_score = int(total_weight * 80)
        
        # Sort signals by severity
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        all_signals.sort(key=lambda s: (severity_order.get(s.get('severity', 'LOW'), 3), -s.get('weight', 0)))
        
        return {
            'risk_score': risk_score,  # 0-100
            'risk_level': risk_level,  # LOW, MEDIUM, HIGH, CRITICAL
            'total_weight': round(total_weight, 2),
            'signal_count': len(all_signals),
            'signals': all_signals,
            'calculated_at': datetime.now().isoformat()
        }
    
    async def analyze_care_home_financial_health(self, company_number: str) -> Dict:
        """
        Complete financial health analysis pipeline
        
        Returns comprehensive risk assessment with all signals
        """
        print(f"Analyzing {company_number}...")
        
        # 1. Fetch all data
        profile = await self.get_company_profile(company_number)
        if not profile:
            return {'error': 'Company not found or API error'}
        
        filings = await self.get_filing_history(company_number, items_per_page=100)
        charges = await self.get_charges(company_number)
        officers = await self.get_company_officers(company_number)
        pscs = await self.get_persons_with_significant_control(company_number)
        
        # 2. Run interpretations
        profile_analysis = self.interpret_company_profile(profile)
        filing_analysis = self.analyze_filing_patterns(filings, profile)
        charge_analysis = self.analyze_debt_structure(charges)
        officer_analysis = self.analyze_director_turnover(officers, filings)
        psc_analysis = self.analyze_ownership_structure(pscs)
        
        # 3. Calculate composite risk score
        risk_assessment = self.calculate_composite_risk_score(
            profile_analysis,
            filing_analysis,
            charge_analysis,
            officer_analysis,
            psc_analysis
        )
        
        # 4. Generate recommendations
        recommendations = self.generate_recommendations(risk_assessment)
        
        return {
            'company_number': company_number,
            'company_name': profile.get('company_name'),
            'analysis_date': datetime.now().isoformat(),
            
            'risk_assessment': risk_assessment,
            
            'data_summary': {
                'company_status': profile.get('company_status'),
                'accounts_overdue': profile.get('accounts', {}).get('overdue', False),
                'total_charges': len(charges),
                'active_directors': officer_analysis.get('active_directors'),
                'ownership_type': 'Private Equity' if psc_analysis['private_equity_indicators'] 
                                 else 'Offshore' if psc_analysis['offshore_entities']
                                 else 'Standard'
            },
            
            'recommendations': recommendations,
            
            'raw_data': {
                'profile': profile,
                'filing_count': len(filings),
                'charge_count': len(charges),
                'officer_count': len(officers),
                'psc_count': len(pscs)
            }
        }
    
    def generate_recommendations(self, risk_assessment: Dict) -> List[str]:
        """Generate actionable recommendations based on risk level"""
        
        risk_level = risk_assessment['risk_level']
        recommendations = []
        
        if risk_level == 'CRITICAL':
            recommendations = [
                'IMMEDIATE ACTION REQUIRED: Consider alternative care homes',
                'Contact local authority for emergency placement options',
                'Document all care quality issues for potential complaint',
                'Prepare for potential facility closure within 3-6 months'
            ]
        elif risk_level == 'HIGH':
            recommendations = [
                'Closely monitor this facility (weekly checks recommended)',
                'Schedule in-person visit to assess operational condition',
                'Begin researching alternative care home options',
                'Set up alerts for CQC rating changes'
            ]
        elif risk_level == 'MEDIUM':
            recommendations = [
                'Continue regular monitoring (monthly checks sufficient)',
                'Review CQC reports when published',
                'Stay informed about facility changes',
                'Have backup options identified'
            ]
        else:  # LOW
            recommendations = [
                'Standard monitoring adequate (quarterly checks)',
                'Facility appears financially stable',
                'Continue routine care quality monitoring'
            ]
        
        return recommendations
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

