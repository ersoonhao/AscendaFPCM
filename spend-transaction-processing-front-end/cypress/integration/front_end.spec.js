const url = "http://cs301-g4t2-2022-frontend.s3-website-ap-southeast-1.amazonaws.com/"

describe ('Test!!!', () => {
    it ('is working', () => {
      expect (true).to.equal (true);
    });
  });

describe ('Test client transaction page', () => {
    it ('Test client transaction page ', () => {
      cy.visit ('/');
      cy.contains("SPEND TRANSACTION PROCESSING")
      cy.contains("Transaction Summary")
      cy.contains("Date")
      cy.contains("Type")
      cy.contains("Rewards Transacted")
      cy.contains("Customer ID")
      // cy.get('input[type="text"]').type("b044eeea-5818-461b-a005-372b0ee53647").should('have vale',"b044eeea-5818-461b-a005-372b0ee53647").trigger('keydown', {
      //   key: 'Enter',
      // })
      // cy.contains('Successfully retrieved all customer transactions!')
      // cy.contains("View Details")
      // cy.get('[data-testid="KeyboardArrowDownIcon"]').first().click()
      // cy.contains("Hide Details")
    });
  });


describe ('Test Campaigns Management page', () => {
    it ('Test Campaigns Management page ', () => {
      cy.visit ('/');
      cy.contains("SPEND TRANSACTION PROCESSING")
      cy.contains("Campaigns Management").click()
      cy.contains("Existing campaigns")
      cy.get('svg[data-testid="RefreshIcon"]').click()
      cy.contains('ID')
      cy.contains('Card Type')
      cy.contains('Description')
      cy.contains('per Dollar Spend')
      cy.contains('Reward')
      cy.contains('Reward Currency')
      cy.contains('MCC')
      cy.contains('Minimum Spend')
      cy.contains('End Date')
      cy.contains('Campaign Status')
    });
});

describe ('Test Upload page', () => {
    it ('Test Upload User File ', () => {
      cy.visit ('/');
      cy.contains("SPEND TRANSACTION PROCESSING")
      cy.contains("Upload").click()
      cy.contains("Upload User")
      cy.contains("Drag and drop user file here, or click to select file")
    });

    it ('Test Upload Spend File ', () => {
        cy.visit ('/');
        cy.contains("SPEND TRANSACTION PROCESSING")
        cy.contains("Upload").click()
        cy.contains("Upload Transactions")
        cy.contains("Drag and drop user file here, or click to select file")
      });

});

