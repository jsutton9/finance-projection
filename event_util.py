def enscope(f, args):
    return lambda: f(*args)

def pegTaxesToInflation(scenario, tax, firstYear, lastYear, deflator):
    initialIncomeBrackets = tax.federalIncomeBrackets
    initialCapitalGainsBrackets = tax.federalCapitalGainsBrackets
    initialDeduction = tax.federalDeduction
    initialSocialSecurityCap = tax.socialSecurityWageBase
    initial401kCap = tax.k401Limit
    initialIraCap = tax.iraLimit
    for year in xrange(firstYear, lastYear+1):
        incomeBrackets = []
        for bracket in initialIncomeBrackets:
            incomeBrackets.append((bracket[0]*deflator(year), bracket[1]))
        gainsBrackets = []
        for bracket in initialCapitalGainsBrackets:
            gainsBrackets.append((bracket[0]*deflator(year), bracket[1]))
        deduction = initialDeduction*deflator(year)
        scenario.addEvent("%d-01-01" % year,
                enscope(tax.setFederalTax, [incomeBrackets, gainsBrackets, deduction]))
        socialSecurityCap = initialSocialSecurityCap*deflator(year)
        scenario.addEvent("%d-01-01" % year,
                enscope(tax.setSocialSecurityTax, [tax.socialSecurityRate, socialSecurityCap]))

def pegRetirementContributionsToInflation(
        scenario, tax, base401k, baseIra, firstYear, lastYear, deflator):
    for year in xrange(firstYear, lastYear+1):
        k401 = base401k*deflator(year)
        ira = baseIra*deflator(year)
        scenario.addEvent("%d-01-01" % year, enscope(tax.setRetirementLimits, [k401, ira]))

def growIncome(scenario, initialDeflatedIncome, rate, deflator, firstYear, lastYear, month=1):
    for year in xrange(firstYear, lastYear+1):
        scenario.addPayChange("%d-%02d-01" % (year, month),
                initialDeflatedIncome*(1+rate)**(year-firstYear)*deflator(year))

def growExpenses(
        scenario, initialDeflatedExpenses, rate, deflator, firstYear, lastYear, month=1):
    for year in xrange(firstYear, lastYear+1):
        scenario.addExpenseChange("%d-%02d-01" % (year, month),
                initialDeflatedExpenses*(1+rate)**(year-firstYear)*deflator(year))

def zeroTax(scenario, dateString):
    def f():
        tax = scenario.taxPolicy
        tax.setFederalTax([[float("inf"), 0]], [[float("inf"), 0]], 0)
        tax.setStateTax(0.0)
        tax.setCityTax(0.0)
        tax.setSocialSecurityTax(0.0, 0)
    scenario.addEvent(dateString, f)

def getDeflator(rate, initialYear):
    return lambda year: (1+rate)**(year-initialYear)

def growReturnRate(scenario, initialRate, otherRate, firstYear, otherYear, lastYear):
    for year in xrange(firstYear, lastYear+1):
        r = float(year-firstYear)/(otherYear-firstYear)
        rate = (1-r)*initialRate + r*otherRate
        scenario.addRateChange("%d-01-01" % year, rate)
