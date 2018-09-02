DAYS_PER_YEAR = 365.2425

INCOME_TAX_BRACKETS_2018 = [
        [9525, .1],
        [38700, 0.12],
        [82500, .22],
        [157500, .24],
        [200000, .32],
        [500000, .35],
        [float("inf"), .37]
    ]

CAPITAL_GAINS_TAX_BRACKETS_2018 = [
        [38600, 0.],
        [425800, .15],
        [float("inf"), .2]
    ]

DEDUCTION_2018 = 12000
PA_TAX_2018 = 0.037
PIT_TAX_2018 = 0.03
SS_TAX_2018 = 0.062
SS_CAP_2018 = 127200
K401_LIMIT_2018 = 18500
IRA_LIMIT_2018 = 5500

class TaxPolicy:
    def __init__(self):
        self.federalIncomeBrackets = []
        self.federalCapitalGainsBrackets = []
        self.federalDeduction = 0.0
        self.stateRate = 0.0
        self.cityRate = 0.0
        self.socialSecurityRate = 0.0
        self.socialSecurityWageBase = 0.0
        self.k401Limit = 0.0
        self.iraLimit = 0.0

        self.totalPay = 0.0
        self.totalCapitalGains = 0.0
        self.withheld = 0.0

        self.lastLiability = 0.0

    def setFederalTax(self, incomeBrackets, capitalGainsBrackets, deduction):
        self.federalIncomeBrackets = incomeBrackets
        self.federalCapitalGainsBrackets = capitalGainsBrackets
        self.federalDeduction = deduction

    def setStateTax(self, rate):
        self.stateRate = rate

    def setCityTax(self, rate):
        self.cityRate = rate

    def setSocialSecurityTax(self, rate, wageBase):
        self.socialSecurityRate = rate
        self.socialSecurityWageBase = wageBase

    def setRetirementLimits(self, k401Limit, iraLimit):
        #print "limits", k401Limit, iraLimit
        self.k401Limit = k401Limit
        self.iraLimit = iraLimit

    def federalIncomeTax(self, taxablePay):
        if taxablePay < 0:
            return 0.0

        liability = 0.0
        previousCap = 0.0
        for cap, rate in self.federalIncomeBrackets:
            liability += (min(taxablePay, cap) - previousCap)*rate
            if taxablePay <= cap:
                break
            previousCap = cap

        return liability

    def federalCapitalGainsTax(self, taxablePay, capitalGains):
        taxableGains = capitalGains
        if taxablePay < 0:
            taxableGains -= taxablePay
            taxablePay = 0.0

        liability = 0.0
        previousCap = 0.0
        for cap, rate in self.federalCapitalGainsBrackets:
            inBracket = min(taxablePay+taxableGains, cap) - max(taxablePay, previousCap)
            if inBracket > 0:
                liability += inBracket*rate
            if taxablePay < cap:
                break

        return liability

    def stateTax(self, taxablePay, capitalGains):
        return (taxablePay + capitalGains)*self.stateRate

    def cityTax(self, taxablePay):
        return taxablePay*self.cityRate

    def socialSecurityTax(self, taxablePay):
        taxableIncome = min(taxablePay, self.socialSecurityWageBase)
        return taxableIncome*self.socialSecurityRate

    def withhold(self, pay):
        self.totalPay += pay
        expectedPay = pay*DAYS_PER_YEAR
        expectedTaxablePay = expectedPay - self.federalDeduction
        k401 = min(expectedTaxablePay, self.k401Limit)
        expectedTaxablePay -= k401
        ira = min(expectedTaxablePay, self.iraLimit)
        expectedTaxablePay -= ira

        withholding = (self.federalIncomeTax(expectedTaxablePay) \
                        + self.stateTax(expectedTaxablePay, 0) \
                        + self.cityTax(expectedTaxablePay) \
                        + self.socialSecurityTax(expectedTaxablePay)) \
                      /DAYS_PER_YEAR
        self.withheld += withholding

        return pay - withholding

    def recordCapitalGains(self, capitalGains):
        self.totalCapitalGains += capitalGains

    def refund(self):
        taxablePay = max(0, self.totalPay - self.federalDeduction)
        k401 = min(taxablePay, self.k401Limit)
        taxablePay -= k401
        ira = min(taxablePay, self.iraLimit)
        taxablePay -= ira
        liability = self.federalIncomeTax(taxablePay) \
                  + self.federalCapitalGainsTax(taxablePay, self.totalCapitalGains) \
                  + self.stateTax(taxablePay, self.totalCapitalGains) \
                  + self.cityTax(taxablePay) \
                  + self.socialSecurityTax(taxablePay)
        refund = self.withheld - liability
        #print self.totalPay, taxablePay, self.totalCapitalGains
        #print self.federalIncomeTax(taxablePay), \
        #        self.federalCapitalGainsTax(taxablePay, self.totalCapitalGains), \
        #        self.stateTax(taxablePay, self.totalCapitalGains), \
        #        self.cityTax(taxablePay), \
        #        self.socialSecurityTax(taxablePay)
        #print "refund = %f = %f - %f" % (refund, self.withheld, liability)
        #print k401, ira

        self.totalPay = 0.0
        self.totalCapitalGains = 0.0
        self.withheld = 0.0

        self.lastLiability = liability

        return refund, k401, ira
