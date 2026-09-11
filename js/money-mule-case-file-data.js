window.MMC_DATA = {
  stages: {
    2: {
      alert: {
        heading: 'The Alert',
        paragraphs: [
          'At 16:52 on Thursday, the fraud operations queue generates a high priority receiving account alert.',
          'Customer R has received £11,420 from four previously unseen individuals in four days.',
          '£10,200 has already moved onwards.',
          'Three new beneficiaries have been used.',
          'One transaction involved a cash withdrawal.',
          'The payment pattern is materially different from Customer R’s established account behaviour.',
          'A sending institution has separately notified the firm that one of the inbound payments originated from an authorised push payment fraud victim.',
          'The transactions require investigation.',
          'They do not yet establish Customer R’s intent.'
        ]
      },
      profile: {
        heading: 'Customer profile',
        fields: [
          { label: 'Customer', value: 'Customer R' },
          { label: 'Age', value: '24' },
          { label: 'Account tenure', value: '3 years and 2 months' },
          { label: 'Primary account use', value: 'Salary, rent, groceries, card spending and ordinary transfers' },
          { label: 'Previous average monthly credits', value: 'Approximately £1,730' },
          { label: 'Employment position', value: 'Temporary employment ended seven weeks ago' },
          { label: 'Recent income', value: 'Materially reduced' },
          { label: 'Previous comparable payment behaviour', value: 'None identified' },
          { label: 'Previous confirmed fraud', value: 'None identified' },
          { label: 'Previous National Fraud Database record', value: 'None identified' },
          { label: 'Recorded vulnerability', value: 'None currently recorded' }
        ],
        vulnerabilityCallout: 'The absence of a previously recorded vulnerability is not evidence that no vulnerability exists.'
      },
      chronology: [
        {
          day: 1,
          incoming: { sender: 'Sender A', amount: 2850 },
          outgoing: { type: 'transfer', beneficiary: 'new beneficiary', amount: 2500 },
          timeToMoveLabel: 'Time to onward movement',
          timeToMove: '26 minutes'
        },
        {
          day: 2,
          incoming: { sender: 'Sender B', amount: 3200 },
          outgoing: { type: 'transfer', beneficiary: 'new beneficiary', amount: 3000 },
          timeToMoveLabel: 'Time to onward movement',
          timeToMove: '19 minutes'
        },
        {
          day: 3,
          incoming: { sender: 'Sender C', amount: 1760 },
          outgoing: { type: 'withdrawal', beneficiary: null, amount: 1500 },
          timeToMoveLabel: 'Time to withdrawal',
          timeToMove: '36 minutes'
        },
        {
          day: 4,
          incoming: { sender: 'Sender D', amount: 3610 },
          outgoing: { type: 'transfer', beneficiary: 'new beneficiary', amount: 3200 },
          timeToMoveLabel: 'Time to onward movement',
          timeToMove: '16 minutes'
        }
      ],
      totals: { received: 11420, moved: 10200, difference: 1220 },
      suggestedHypotheses: { A: 'Plausible', B: 'Unresolved', C: 'Plausible', D: 'Unresolved', E: 'Plausible' },
      gateNote: 'The practitioner must review all five hypotheses before continuing.',
      practitionerLensIntro: 'What can you actually establish at this stage?',
      practitionerLensCanEstablish: [
        'You can establish that unusual funds entered the account.',
        'You can establish that most were moved rapidly.',
        'You can establish that the behaviour materially differs from the customer’s historical activity.',
        'You can establish that at least one sending institution has reported fraud.'
      ],
      practitionerLensCannotEstablish: [
        'You cannot yet establish who controlled the transactions.',
        'You cannot establish what Customer R believed.',
        'You cannot establish why Customer R moved the funds.',
        'You cannot establish whether Customer R received a benefit knowingly.',
        'You cannot establish whether somebody else influenced or controlled the activity.'
      ],
      practitionerLensClosing: 'Do not let the transaction pattern answer a customer intent question that has not yet been investigated.'
    },
    3: {
      customerExplanation: {
        intro: [
          'Customer R is contacted.',
          'They sound anxious but cooperate.',
          'They explain that approximately two weeks earlier they responded to an advertisement for remote work.'
        ],
        roleTitle: 'Client Settlement Assistant',
        roleParagraphs: [
          'Customer R says the role involved administrative support and processing payments received from clients.',
          'They were told the company was expanding its UK operation and that new staff would temporarily use personal accounts to process client settlements while additional corporate payment facilities were being established.'
        ]
      },
      provided: [
        'A screenshot of the original job advertisement.',
        'An employment agreement.',
        'A link to a professional looking company website.',
        'WhatsApp communications with someone identifying themselves as an operations manager.',
        'Payment instructions.',
        'A document explaining how staff commission would be calculated.'
      ],
      retainedFundsExplanation: 'Customer R says the £1,220 difference between received and onward funds represented wages, commission and amounts they were instructed to retain pending reconciliation.',
      framingLine: 'At this point these documents establish what Customer R claims happened. They do not establish that the employment was genuine.',
      evidenceItems: [
        { title: 'Customer account of recruitment', status: 'SelfReported' },
        { title: 'Job advertisement screenshot', status: 'SelfReported', note: 'Authenticity not yet established.' },
        { title: 'Employment agreement', status: 'SelfReported', note: 'Authenticity not yet established.' },
        { title: 'Website', status: 'Observed' },
        { title: 'WhatsApp conversation', status: 'SelfReported', note: 'Metadata not yet verified.' },
        { title: 'Payment instruction documents', status: 'SelfReported' },
        { title: 'Claimed commission arrangement', status: 'SelfReported' }
      ],
      hypothesisImpact: {
        A: 'Weakened slightly',
        B: 'Still unresolved',
        C: 'Strengthened',
        D: 'Still uncertain',
        E: 'Weakened if the customer’s explanation is accurate'
      },
      practitionerLens: {
        heading: 'Do not ask whether the documents look professional. Ask whether they can be independently authenticated.',
        body: 'Deceptive employment propositions can include professional looking websites, documentation, interviews and structured onboarding.',
        closing: 'What would you authenticate before deciding whether this employment explanation is genuine?'
      },
      investigationActions: [
        'Verify company registration and trading history.',
        'Verify domain registration history.',
        'Examine message metadata.',
        'Verify recruiter identity.',
        'Compare beneficiary instructions against transaction records.',
        'Check whether the supposed employer has genuine corporate payment infrastructure.',
        'Review whether recruitment materials existed before suspicious activity began.'
      ],
      investigationActionsNote: 'These are reflective prompts only. No selection is scored, recorded or marked correct or incorrect.'
    },
    4: {
      digitalEvidence: {
        paragraphs: [
          'Internal authentication records become available.',
          'All four relevant sessions originated from Customer R’s established mobile device.',
          'The device had been associated with the account for seventeen months.',
          'Normal biometric authentication was used.',
          'There were no password resets immediately before the activity.',
          'There were no newly registered devices.',
          'There was no material change in the normal geographic pattern of account access.',
          'Customer R manually created the new beneficiaries.',
          'Customer R personally confirmed the relevant transfers.',
          'The beneficiary details match instructions contained within the WhatsApp conversation supplied by Customer R.'
        ]
      },
      evidenceItems: [
        { title: 'Established device', status: 'Observed' },
        { title: 'Biometric authentication', status: 'Observed' },
        { title: 'Normal access geography', status: 'Observed' },
        { title: 'Beneficiary creation', status: 'Observed' },
        { title: 'Transfer authorisation', status: 'Observed' },
        { title: 'Beneficiary details matching supplied communications', status: 'Corroborated' }
      ],
      coreMessage: 'Control has become clearer. Intent has not.',
      practitionerLens: {
        heading: 'This evidence answers who performed the account actions. It does not answer why they performed them.',
        body: 'Authentication establishes control much more strongly than intent.'
      },
      gateNote: 'Review all five hypotheses again in light of this evidence before continuing.'
    },
    5: {
      intro: [
        'This compares your initial assessment against your current assessment.',
        'It does not reveal FinCrimeRadar’s own position on the five hypotheses.'
      ]
    },
    6: {
      messageHistory: {
        heading: 'The messages change the picture',
        paragraphs: [
          'The complete message history is obtained and timestamps are verified.',
          'The early communications appear consistent with Customer R’s explanation.',
          'The recruiter discusses employment.',
          'Customer R asks about working hours.',
          'The recruiter explains payment processing procedures.',
          'Customer R submits identity documents and bank details as part of the supposed onboarding process.',
          'Then the character of the conversation begins to change.',
          'After the second incoming payment, Customer R asks why money is arriving from different individuals rather than the company.',
          'The recruiter replies that the payments come directly from clients.',
          'Customer R asks why the company cannot receive the money itself.',
          'The recruiter says the corporate settlement account is undergoing an upgrade.',
          'Before the third transaction, Customer R writes:'
        ],
        quote: 'Something about this feels wrong. Why am I moving other people’s money through my own account?',
        paragraphsAfterQuote: [
          'The recruiter reassures Customer R that the process is legal and covered by the employment agreement.',
          'Customer R completes the third transaction.',
          'Later that evening Customer R searches online for phrases relating to receiving company payments into a personal bank account.',
          'No contact with the bank is made.'
        ]
      },
      evidenceItems: [
        { title: 'Early recruitment conversations', status: 'Corroborated' },
        { title: 'Questions about source of payments', status: 'Corroborated' },
        { title: 'Expressed concern', status: 'Corroborated' },
        { title: 'Recruiter reassurance', status: 'Corroborated' },
        {
          title: 'Third transaction after concern',
          status: 'Corroborated',
          note: 'Also directly observed in the transaction records.'
        },
        { title: 'Relevant internet searches', status: 'Observed' },
        { title: 'No bank contact at this point', status: 'Observed' }
      ],
      timelineProblem: {
        heading: 'The Timeline Problem',
        intro: 'This is the first major conceptual turn.',
        display: 'The evidence increasingly supports the proposition that Customer R initially believed the arrangement might be legitimate. It also shows that their understanding was changing.'
      },
      timelineAssessment: {
        heading: 'Timeline assessment',
        intro: 'The practitioner must separately assess:',
        questions: [
          { key: 'entryState', label: 'Likely state at entry' },
          { key: 'prePaymentThreeState', label: 'Likely state before Payment Three' }
        ],
        note: 'These are investigative assessments. Do not present them as legal conclusions.'
      },
      changePointQuestion: {
        label: 'At what point did Customer R’s understanding materially change?',
        optionIds: ['initialRecruitment', 'paymentOne', 'paymentTwo', 'concernEmerges', 'paymentThree']
      },
      gateNote: 'Record all three timeline assessments before continuing.'
    },
    7: {
      disengagement: {
        paragraphs: [
          'On the morning of Day 4, before the fourth incoming payment, Customer R tells the recruiter:'
        ],
        quoteOne: 'I am not doing any more transfers until somebody explains what this actually is.',
        paragraphsAfterQuoteOne: [
          'The recruiter immediately calls Customer R several times.',
          'Customer R does not initially answer.',
          'The recruiter then sends a copy of the identity document Customer R supplied during recruitment.',
          'They refer to Customer R’s home postcode.',
          'They state that Customer R is responsible for money already processed and will face serious consequences if the work is abandoned.',
          'The recruiter states that the company knows where Customer R lives.',
          'Over the next several hours, seventeen attempted calls are recorded.',
          'Customer R sends a message to a close friend:'
        ],
        quoteTwo: 'I think I\'ve got involved in something bad. I\'m trying to stop and they\'re threatening me.',
        paragraphsAfterQuoteTwo: [
          'The message to the friend was sent before the fourth transfer and before the bank contacted Customer R.',
          'The recruiter continues demanding completion of the fourth transfer.',
          'Customer R eventually makes the transfer.'
        ]
      },
      evidenceItems: [
        { title: 'Attempt to stop participating', status: 'Corroborated' },
        { title: 'Escalating recruiter contact', status: 'Corroborated' },
        { title: 'Use of personal information', status: 'Corroborated' },
        { title: 'Threatening language', status: 'Corroborated' },
        { title: 'Message to friend', status: 'Corroborated', note: 'Independently timestamped.' },
        { title: 'Message predates institutional intervention', status: 'Corroborated' },
        { title: 'Fourth transaction', status: 'Observed' },
        { title: 'Transaction occurred after threatening communications', status: 'Corroborated' }
      ],
      timelineRevealIds: ['initialRecruitment', 'paymentOne', 'paymentTwo', 'concernEmerges', 'paymentThree', 'attemptedExit', 'threats', 'paymentFour', 'intervention'],
      questions: [
        { key: 'controlDecision', label: 'Did Customer R control Payment Four?' },
        { key: 'voluntarinessDecision', label: 'Does the available evidence establish that Payment Four was freely voluntary?' }
      ],
      coercionCallout: 'Control and voluntariness are not the same thing.',
      hypothesisImpact: {
        A: 'Remains possible for part of the timeline',
        B: 'Strongly supported',
        C: 'Strongly supported at initial entry',
        D: 'Materially strengthened',
        E: 'Very weak'
      },
      gateNote: 'Record both decisions and confirm all five hypotheses before continuing.'
    },
    8: {
      narrative: {
        heading: 'Independent corroboration',
        paragraphs: [
          'External enquiries return.',
          'The supposed employer has no verified relationship with the payment activity.',
          'The website used during recruitment was registered shortly before the recruitment campaign began.',
          'The business details shown to Customer R cannot be verified as belonging to the recruiter.',
          'All four incoming transactions are subsequently confirmed by sending institutions as connected to reported fraud.',
          'One onward beneficiary is linked by another institution to a wider suspected receiving account network.',
          'No evidence is found that Customer R recruited another participant.',
          'No earlier comparable receiving activity is found across Customer R’s three year account history.',
          'No previous fraud database record is identified.',
          'The original job advertisement predates the suspicious transactions.',
          'The early recruiter conversations predate the suspicious transactions.',
          'Customer R’s message to their friend describing concern and threats predates the bank intervention.',
          'The retained £1,220 is identifiable within the account history.',
          'Part was subsequently used for ordinary living expenditure.',
          'No evidence currently establishes that Customer R negotiated a percentage of criminal proceeds outside the employment explanation already supplied.'
        ]
      },
      evidenceItems: [
        { title: 'Criminal provenance of inbound funds', status: 'Corroborated' },
        { title: 'False employment proposition', status: 'Corroborated' },
        { title: 'Recruitment evidence predating activity', status: 'Corroborated' },
        { title: 'Customer concern predating intervention', status: 'Corroborated' },
        { title: 'Threat evidence predating intervention', status: 'Corroborated' },
        { title: 'Customer control of transactions', status: 'StronglyCorroborated' },
        { title: 'Wider beneficiary risk', status: 'Corroborated' },
        { title: 'Prior similar behaviour', status: 'NotIdentified' },
        { title: 'Recruitment of others', status: 'NotIdentified' },
        { title: 'Deliberately negotiated criminal commission', status: 'NotEstablished' }
      ],
      freezeNote: 'No further evidence will be introduced after this stage.'
    },
    9: {
      intro: [
        'Classify all five hypotheses one final time, drawing on everything now on the case file.',
        'Once you confirm, this compares your initial assessment against your final assessment.',
        'It does not yet reveal FinCrimeRadar’s own conclusion on the five hypotheses.'
      ],
      gateNote: 'Record your final position on all five hypotheses before confirming.'
    },
    10: {
      intro: [
        'The practitioner must make findings separately across each of the five dimensions below.',
        'The question is not: is Customer R a money mule?',
        'Independent findings are required instead.'
      ],
      dimensions: [
        {
          id: 'activity',
          question: 'What happened through the account?',
          options: ['Confirmed', 'Partially confirmed', 'Not established', 'Cannot determine'],
          fincrimeradarAnalysis: 'Confirmed. The account received proceeds connected to reported fraud and rapidly moved most of those funds onwards.'
        },
        {
          id: 'control',
          question: 'Who controlled the relevant account activity?',
          options: ['Strongly established', 'Partially established', 'Not established', 'Cannot determine'],
          fincrimeradarAnalysis: 'Strongly established. Customer R controlled the device and authorised the transactions.'
        },
        {
          id: 'knowledge',
          question: 'What did Customer R understand, and when?',
          options: ['Established from entry', 'Developed during the timeline', 'Not established', 'Cannot determine'],
          fincrimeradarAnalysis: 'Time dependent. The evidence supports initial deception. It later establishes growing concern and suspicion. It does not establish that Customer R entered the arrangement with knowledge of its criminal purpose.'
        },
        {
          id: 'exploitation',
          question: 'Was Customer R manipulated, pressured or coerced?',
          options: ['Materially supported', 'Some indicators, not conclusive', 'Not supported', 'Cannot determine'],
          fincrimeradarAnalysis: 'Materially supported. Later communications contain credible and independently timestamped indicators of intimidation and coercive pressure.'
        },
        {
          id: 'evidence',
          question: 'What can actually be demonstrated?',
          options: ['Strong across all dimensions', 'Strong for some, incomplete for others', 'Weak overall', 'Cannot determine'],
          fincrimeradarAnalysis: 'Strong for account activity and customer control. Strong for the existence of the deceptive recruitment process. Strong for changing customer suspicion. Strong for later threatening communications. Incomplete regarding the precise point at which Customer R believed, rather than merely suspected, that the funds represented criminal proceeds.'
        }
      ],
      operationalDecisions: [
        {
          title: 'Immediate account intervention',
          position: 'Supported.',
          paragraphs: [
            'The institution has strong evidence that its facilities are being used to move fraud proceeds.',
            'Customer intent does not need to be conclusively resolved before proportionate measures are taken to prevent further movement and investigate the activity.'
          ]
        },
        {
          title: 'Recovery and network investigation',
          position: 'Supported.',
          paragraphs: [
            'The sending institutions and onward beneficiaries provide opportunities for recovery, disruption and wider network intelligence.'
          ]
        },
        {
          title: 'Suspicious Activity Report consideration',
          position: 'Strongly engaged.',
          paragraphs: [
            'The account activity, criminal provenance of funds and connected beneficiary intelligence create significant money laundering suspicion.',
            'The SAR assessment must not depend on first proving that Customer R is a knowing criminal participant.',
            'Customer circumstances, recruiters, accounts, devices, beneficiaries and relevant exploitation indicators may themselves provide useful intelligence.',
            'This analysis is not legal advice.'
          ]
        },
        {
          title: 'Safeguarding assessment',
          position: 'Required.',
          paragraphs: [
            'Evidence of threats and exploitation should trigger appropriate safeguarding consideration rather than being treated merely as mitigation within a fraud investigation.'
          ]
        },
        {
          title: 'National Fraud Database assessment',
          position: 'Not automatic.',
          paragraphs: [
            'This decision requires its own evidential assessment.',
            'Suspicious transaction behaviour and mule detection alerts do not automatically satisfy the evidential requirements for a National Fraud Database filing.',
            'The FCA has stated that firms must obtain sufficient evidence concerning customer involvement and knowledge and has highlighted the difficulty of establishing willing participation.',
            'Cifas requires clear, relevant and rigorous evidence, satisfaction of the applicable case criteria, accuracy and proportional interpretation.',
            'Financial Ombudsman material here is practical complaint handling guidance and case reasoning, not legislation or binding precedent.'
          ]
        }
      ],
      closingLine: 'Account restriction, customer exit, SAR consideration, safeguarding and fraud database filing are separate decisions with different purposes and evidential questions.',
      gateNote: 'Record a finding on all five dimensions before continuing.'
    },
    11: {
      intro: 'The final FinCrimeRadar analysis remains locked until the practitioner has considered each challenge below.',
      redTeamQuestions: [
        { key: 'transactionBias', category: 'Transaction bias', question: 'Have you treated rapid movement as evidence of intent rather than evidence of activity?' },
        { key: 'authenticationBias', category: 'Authentication bias', question: 'Have you mistaken customer authentication for proof of voluntary criminal participation?' },
        { key: 'outcomeBias', category: 'Outcome bias', question: 'Has confirmation that the funds were criminal changed how you judge what Customer R could reasonably have known earlier?' },
        { key: 'vulnerabilityBias', category: 'Vulnerability bias', question: 'Are you assuming that exploitation eliminates all personal agency?' },
        { key: 'culpabilityBias', category: 'Culpability bias', question: 'Are you assuming that continued participation eliminates the possibility of exploitation?' },
        { key: 'narrativeBias', category: 'Narrative bias', question: 'Have you accepted Customer R’s explanation merely because it is coherent?' },
        { key: 'suspicionThreshold', category: 'Suspicion threshold', question: 'Can you identify the evidence showing when suspicion actually emerged?' },
        { key: 'corroboration', category: 'Corroboration', question: 'Which parts of the customer account exist independently of what Customer R later told the bank?' },
        { key: 'counterfactual', category: 'Counterfactual', question: 'What evidence would make you reach the opposite conclusion?' },
        { key: 'proportionality', category: 'Proportionality', question: 'Are your operational actions based on the risk that must be controlled, or on a label applied to the customer?' }
      ],
      decisionChangeIntro: 'A strong investigation identifies not only what supports the current conclusion, but also what evidence could materially change it.',
      decisionChangeItems: [
        { key: 'item1', text: 'Evidence that Customer R discussed the criminal source of funds before Payment One.' },
        { key: 'item2', text: 'Evidence that Customer R negotiated payment specifically for laundering criminal proceeds.' },
        { key: 'item3', text: 'Evidence that Customer R recruited other account holders.' },
        { key: 'item4', text: 'Evidence of earlier comparable episodes.' },
        { key: 'item5', text: 'Evidence that the recruitment communications were fabricated after bank intervention.' },
        { key: 'item6', text: 'Evidence showing that the threatening communications were fabricated.' },
        { key: 'item7', text: 'Evidence that another person remotely controlled the account.' },
        { key: 'item8', text: 'Evidence that Customer R attempted to contact the bank before completing Payment Three.' },
        { key: 'item9', text: 'Evidence showing continued voluntary participation after the threats ceased.' }
      ],
      reasoningShiftQuestion: 'Did the evidence change your view of Customer R during the investigation?',
      reasoningShiftOptions: [
        { label: 'Substantially', value: 'Substantially' },
        { label: 'Somewhat', value: 'Somewhat' },
        { label: 'No Material Change', value: 'NoMaterialChange' }
      ],
      gateNote: 'Complete the Red Team Review and record whether the evidence changed your view before continuing.'
    },
    12: {
      radar: {
        dimensions: [
          { heading: 'Activity', summary: 'Strong evidence of movement of fraud proceeds' },
          { heading: 'Control', summary: 'Strong evidence of customer transaction control' },
          { heading: 'Knowledge', summary: 'Initially weak, later materially increased' },
          { heading: 'Exploitation', summary: 'Strong evidence during later activity' },
          { heading: 'Evidence', summary: 'Substantial, but incomplete concerning the precise development of criminal knowledge' }
        ],
        conclusionLine: 'Initial deception → emerging suspicion → continued participation → attempted disengagement → coercive pressure'
      },
      finalAnalysis: {
        caseConclusion: {
          heading: 'The Case Conclusion',
          paragraphs: [
            'The strongest interpretation is not simply:'
          ],
          quoteOne: 'Money mule.',
          paragraphsAfterQuoteOne: [
            'It is also not simply:'
          ],
          quoteTwo: 'Victim.',
          paragraphsAfterQuoteTwo: [
            'The evidence indicates a changing relationship.',
            'Customer R appears to have entered the arrangement through deception.',
            'Questions and inconsistencies subsequently caused suspicion to develop.',
            'Customer R nevertheless continued participating.',
            'Customer R later attempted to disengage.',
            'The recruiter then escalated into threatening and coercive behaviour.',
            'The same customer’s position cannot safely be reduced to one label covering the entire four day period.',
            'The analytical failure would be choosing the label first and then forcing every piece of evidence to support it.',
            'The stronger approach is to reconstruct the customer’s changing position over time.'
          ]
        },
        principle: {
          heading: 'The FinCrimeRadar Principle',
          lines: [
            'Activity tells you what happened.',
            'Control tells you who performed the action.',
            'Knowledge tells you what they understood.',
            'Exploitation tells you what constrained or manipulated their choices.',
            'Evidence tells you what you can defend.'
          ],
          closing: 'A robust investigation does not collapse those questions into a single label.'
        },
        closing: {
          question: 'What did the customer know, what did they control, what influenced their actions, and what can the evidence actually prove at each point in time?',
          line: 'That is the investigation.'
        }
      }
    }
  },
  timelinePoints: [
    { id: 'initialRecruitment', label: 'Initial Recruitment' },
    { id: 'paymentOne', label: 'Payment One' },
    { id: 'paymentTwo', label: 'Payment Two' },
    { id: 'concernEmerges', label: 'Concern Emerges' },
    { id: 'paymentThree', label: 'Payment Three' },
    { id: 'attemptedExit', label: 'Attempted Exit' },
    { id: 'threats', label: 'Threats' },
    { id: 'paymentFour', label: 'Payment Four' },
    { id: 'intervention', label: 'Intervention' }
  ],
  hypotheses: {
    A: {
      name: 'Knowing Participation',
      description: 'The customer understood the illicit nature of the arrangement and deliberately facilitated the movement of funds.'
    },
    B: {
      name: 'Participation After Emerging Suspicion',
      description: 'The customer may not have understood the arrangement initially, but evidence later indicates growing suspicion followed by continued participation. This is an investigative hypothesis, not a declaration of criminal liability.'
    },
    C: {
      name: 'Deceived Participation',
      description: 'The customer genuinely believed the activity had a legitimate explanation such as employment, commerce, investment or helping another person.'
    },
    D: {
      name: 'Financial Exploitation or Coercion',
      description: 'The customer was manipulated, controlled, threatened, groomed or otherwise exploited.'
    },
    E: {
      name: 'Account Compromise',
      description: 'The account holder did not authorise or meaningfully participate in the relevant activity.'
    }
  },
  sources: {}
};
