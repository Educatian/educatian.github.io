(() => {
  "use strict";

  const root = document.documentElement;
  root.classList.add("js");

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  const revealItems = Array.from(document.querySelectorAll(".reveal"));
  if (reducedMotion.matches || !("IntersectionObserver" in window)) {
    revealItems.forEach((item) => item.setAttribute("data-revealed", "true"));
  } else {
    const revealObserver = new IntersectionObserver(
      (entries, observer) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.setAttribute("data-revealed", "true");
          observer.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -8%", threshold: 0.08 }
    );
    revealItems.forEach((item) => revealObserver.observe(item));
  }

  const progressBar = document.querySelector(".reading-progress__bar");
  let progressFrame = 0;
  const updateProgress = () => {
    progressFrame = 0;
    if (!progressBar) return;
    const scrollable = document.documentElement.scrollHeight - window.innerHeight;
    const progress = scrollable > 0 ? Math.min(1, Math.max(0, window.scrollY / scrollable)) : 0;
    progressBar.style.transform = `scaleX(${progress})`;
  };
  const requestProgressUpdate = () => {
    if (progressFrame) return;
    progressFrame = window.requestAnimationFrame(updateProgress);
  };
  updateProgress();
  window.addEventListener("scroll", requestProgressUpdate, { passive: true });
  window.addEventListener("resize", requestProgressUpdate, { passive: true });

  const navDetails = document.querySelector(".project-nav__details");
  const navSummary = navDetails?.querySelector("summary");
  const navLinks = Array.from(document.querySelectorAll(".project-nav__link"));
  const closeMenu = () => {
    if (!navDetails?.open) return;
    navDetails.open = false;
    navSummary?.setAttribute("aria-label", "프로젝트 메뉴 열기");
  };
  navDetails?.addEventListener("toggle", () => {
    navSummary?.setAttribute("aria-label", navDetails.open ? "프로젝트 메뉴 닫기" : "프로젝트 메뉴 열기");
  });
  navLinks.forEach((link) => link.addEventListener("click", closeMenu));
  const desktopNavMedia = window.matchMedia("(min-width: 961px)");
  const syncNavVisibility = (media = desktopNavMedia) => {
    if (!navDetails) return;
    navDetails.open = media.matches;
  };
  syncNavVisibility();
  if (typeof desktopNavMedia.addEventListener === "function") desktopNavMedia.addEventListener("change", syncNavVisibility);
  else desktopNavMedia.addListener(syncNavVisibility);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeMenu();
  });

  const navTargets = navLinks
    .map((link) => document.querySelector(link.getAttribute("href")))
    .filter(Boolean);
  if ("IntersectionObserver" in window && navTargets.length) {
    const activeSections = new Map();
    const navObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => activeSections.set(entry.target.id, entry.intersectionRatio));
        const activeId = Array.from(activeSections.entries())
          .filter(([, ratio]) => ratio > 0)
          .sort((a, b) => b[1] - a[1])[0]?.[0];
        navLinks.forEach((link) => {
          const isActive = link.getAttribute("href") === `#${activeId}`;
          if (isActive) link.setAttribute("aria-current", "true");
          else link.removeAttribute("aria-current");
        });
      },
      { rootMargin: "-20% 0px -58%", threshold: [0, 0.2, 0.45, 0.7] }
    );
    navTargets.forEach((section) => navObserver.observe(section));
  }

  const gallery = document.querySelector("[data-evidence-gallery]");
  const galleryImage = document.querySelector("#evidence-image");
  const galleryTitle = document.querySelector("#evidence-title");
  const galleryDescription = document.querySelector("#evidence-description");
  const galleryTabs = Array.from(gallery?.querySelectorAll("[role='tab']") ?? []);

  const selectEvidence = (tab, moveFocus = false) => {
    if (!galleryImage || !galleryTitle || !galleryDescription) return;
    galleryTabs.forEach((candidate) => {
      const selected = candidate === tab;
      candidate.classList.toggle("is-selected", selected);
      candidate.setAttribute("aria-selected", String(selected));
      candidate.tabIndex = selected ? 0 : -1;
    });

    galleryImage.classList.add("is-changing");
    const applySelection = () => {
      galleryImage.src = tab.dataset.src;
      galleryImage.width = Number(tab.dataset.width);
      galleryImage.height = Number(tab.dataset.height);
      galleryImage.alt = tab.dataset.alt;
      galleryTitle.textContent = tab.dataset.title;
      galleryDescription.textContent = tab.dataset.description;
      const decodeImage = typeof galleryImage.decode === "function" ? galleryImage.decode() : Promise.resolve();
      decodeImage.catch(() => undefined).finally(() => galleryImage.classList.remove("is-changing"));
    };
    if (reducedMotion.matches) applySelection();
    else window.setTimeout(applySelection, 120);
    if (moveFocus) tab.focus();
  };

  galleryTabs.forEach((tab, index) => {
    tab.tabIndex = tab.classList.contains("is-selected") ? 0 : -1;
    tab.addEventListener("click", () => selectEvidence(tab));
    tab.addEventListener("keydown", (event) => {
      if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      let nextIndex = index;
      if (event.key === "Home") nextIndex = 0;
      else if (event.key === "End") nextIndex = galleryTabs.length - 1;
      else if (event.key === "ArrowLeft" || event.key === "ArrowUp") nextIndex = (index - 1 + galleryTabs.length) % galleryTabs.length;
      else nextIndex = (index + 1) % galleryTabs.length;
      selectEvidence(galleryTabs[nextIndex], true);
    });
  });

  const dialog = document.querySelector("#evidence-dialog");
  const dialogImage = document.querySelector("#dialog-image");
  const dialogCaption = document.querySelector("#dialog-caption");
  const openEvidence = document.querySelector("[data-open-evidence]");
  openEvidence?.addEventListener("click", () => {
    if (!dialog || !galleryImage || !dialogImage || !dialogCaption) return;
    dialogImage.src = galleryImage.currentSrc || galleryImage.src;
    dialogImage.width = galleryImage.naturalWidth || galleryImage.width;
    dialogImage.height = galleryImage.naturalHeight || galleryImage.height;
    dialogImage.alt = galleryImage.alt;
    dialogCaption.textContent = galleryTitle?.textContent ?? "프로토타입 화면";
    if (typeof dialog.showModal === "function") dialog.showModal();
  });
  dialog?.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });

  const languagePairs = [
    [`교실을 다시 읽다 | 생성형 AI 교사대응훈련 연구`, `Read the Classroom Again | Generative AI Teacher Response Training Research`],
    [`한국 초등학교 교실을 배경으로 정서·행동 위기 학생 대응 역량을 훈련하는 생성형 AI 통합 Unity 연구 프로토타입과 3개년 연구계획을 소개합니다.`, `Explore a generative AI-integrated Unity research prototype and three-year plan for practicing educator responses to students in emotional and behavioral crisis in Korean elementary classrooms.`],
    [`정서·행동 위기 학생 대응을 안전하게 반복 연습하는 한국 초등학교 기반 Unity 연구 프로토타입과 3개년 연구 로드맵.`, `A Korean elementary classroom Unity prototype and three-year roadmap for safely rehearsing responses to students in emotional and behavioral crisis.`],
    [`한국 초등학교 교실 Unity 시뮬레이션 화면과 교실을 다시 읽다라는 제목`, `A Unity simulation of a Korean elementary classroom with the title “Read the Classroom Again.”`],
    [`한국 초등학교 기반 생성형 AI 통합 교사 대응 훈련 시뮬레이션 연구.`, `A generative AI-integrated teacher-response training simulation grounded in Korean elementary classrooms.`],
    [`본문으로 건너뛰기`, `Skip to content`],
    [`프로젝트 주요 섹션`, `Project sections`],
    [`교실을 다시 읽다`, `Read the Classroom Again`],
    [`교실을 다시 읽다, 페이지 처음으로`, `Read the Classroom Again, back to top`],
    [`영어로 보기`, `Switch to English`],
    [`한국어로 보기`, `Switch to Korean`],
    [`프로젝트 메뉴 열기`, `Open project menu`],
    [`프로젝트 메뉴 닫기`, `Close project menu`],
    [`메뉴`, `Menu`],
    [`취지`, `Purpose`],
    [`프로토타입`, `Prototype`],
    [`연구 트랙`, `Research tracks`],
    [`3개년 로드맵`, `Three-year roadmap`],
    [`연구팀`, `Research team`],
    [`연구 경계`, `Research boundaries`],
    [`생성형 AI × 교사교육`, `Generative AI × Teacher Education`],
    [`교실을`, `Read the`],
    [`다시 읽다`, `Classroom Again`],
    [`교사의 정서행동위기 학생 대응 역량 강화를 위한 생성형 AI 통합 지능형 시뮬레이션 개발`, `Development of a Generative AI-Integrated Intelligent Simulation to Strengthen Educators' Competencies in Responding to Students in Emotional and Behavioral Crisis`],
    [`교사의 정서·행동 위기 학생 대응 역량 강화를 위한 생성형 AI 통합 지능형 시뮬레이션 개발`, `Development of a Generative AI-Integrated Intelligent Simulation to Strengthen Educators' Competencies in Responding to Students in Emotional and Behavioral Crisis`],
    [`정서·행동 위기 신호를 알아차리고, 학급 전체의 흐름을 지키며, 관계를 해치지 않는 개입을 반복해 연습합니다. 실제 학생에게 위험을 전가하지 않는 한국 초등학교 기반 교사교육 연구입니다.`, `Practice noticing emotional and behavioral crisis signals, protecting the flow of the whole class, and choosing relationship-preserving interventions. This teacher-education research is grounded in Korean elementary classrooms without placing real students at risk.`],
    [`프로젝트 핵심 정보`, `Project highlights`],
    [`Unity 6 연구 프로토타입`, `Unity 6 research prototype`],
    [`3개년 연구계획 · 2026–2029`, `Three-year research plan · 2026–2029`],
    [`한국·미국 공동연구`, `Korea–U.S. collaborative research`],
    [`현재 증거 보기`, `View current evidence`],
    [`연구 구조 읽기`, `Read the research structure`],
    [`한국 초등학교 교실을 재현한 Unity 시뮬레이션에서 여러 학생 행동을 관찰하고 교사가 대응 선택지를 고르는 장면`, `A Unity simulation of a Korean elementary classroom where the teacher observes several student behaviors and chooses a response.`],
    [`일반 교실 훈련 장면`, `General classroom training scene`],
    [`Unity 연구 프로토타입 · 2026년 7월 개발 스냅샷`, `Unity research prototype · July 2026 development snapshot`],
    [`현재 구현`, `Implemented`],
    [`Why this project / 연구 취지`, `Why this project / Purpose`],
    [`한 학생의 신호와`, `One student's signals and`],
    [`학급 전체의 흐름을`, `the whole-class flow`],
    [`동시에 본다`, `at once`],
    [`정서·행동 위기 상황에서 교사는 한 학생의 언어, 표정, 몸짓을 읽는 동시에 수업의 안전과 참여를 조율해야 합니다. 이 연구는 그 복합 판단을 지식 암기가 아니라 반복 가능한 경험으로 바꾸려 합니다.`, `In an emotional and behavioral crisis, a teacher must read one student's words, expression, and movement while coordinating safety and participation for the class. This project turns that complex judgment into repeatable experience instead of memorized knowledge.`],
    [`교실 맥락에서 발생하는 다수의 정서·행동 신호를 인지하고, 상황의 우선순위를 판단하며, 개입 시점과 전략을 조율하는 클래스룸 오케스트레이션 역량을 훈련합니다.`, `Train the classroom-orchestration skills needed to recognize multiple emotional and behavioral signals, judge priorities, and coordinate when and how to intervene in context.`],
    [`훈련이 다루는 세 가지 판단`, `Three judgments practiced in training`],
    [`인지`, `Notice`],
    [`말, 시선, 얼굴, 자세, 과제 맥락에서 초기 신호를 구별합니다.`, `Distinguish early signals in speech, gaze, facial expression, posture, and task context.`],
    [`조율`, `Coordinate`],
    [`개입의 우선순위, 시점, 강도를 학급 전체의 흐름과 함께 판단합니다.`, `Judge an intervention's priority, timing, and intensity alongside the flow of the whole class.`],
    [`회복`, `Restore`],
    [`학생의 존엄과 관계를 지키면서 수업 복귀와 후속 지원을 연결합니다.`, `Protect student dignity and relationships while connecting a return to learning with follow-up support.`],
    [`Current evidence / 현재 프로토타입`, `Current evidence / Prototype`],
    [`연구 질문을 먼저`, `Make the research questions`],
    [`작동하는 장면으로`, `visible in a working scene`],
    [`현재 빌드는 관찰, 대응 선택, 직접 대화, 디브리핑의 네 모드를 연결합니다. OpenRouter가 설정되면 생성형 학생 응답을 사용하고, 설정되지 않거나 실패하면 결정론적 로컬 응답으로 전체 훈련을 이어갑니다.`, `The current build connects four modes: observation, response selection, direct dialogue, and debriefing. When OpenRouter is configured it uses generative student responses; when it is unavailable or fails, deterministic local responses keep the training running.`],
    [`검증 기준일 · 2026.07.17`, `Validation snapshot · 2026.07.17`],
    [`현재 프로토타입 지표`, `Current prototype metrics`],
    [`훈련 씬`, `Training scenes`],
    [`일반 교실 + 원형 토론`, `General classroom + circle discussion`],
    [`학생 NPC`, `Student NPCs`],
    [`씬마다 Rocketbox 기반`, `Rocketbox-based in each scene`],
    [`상황 단위`, `Scenario units`],
    [`씬마다 6단계 × 3개 선택지`, `6 stages × 3 choices per scene`],
    [`EditMode 테스트`, `EditMode tests`],
    [`Windows player build 성공`, `Windows player build passed`],
    [`훈련 상호작용 순환`, `Training interaction loop`],
    [`관찰`, `Observe`],
    [`대응`, `Respond`],
    [`대화`, `Dialogue`],
    [`LLM 응답과 선택형 개입`, `LLM response and guided intervention`],
    [`디브리핑`, `Debrief`],
    [`선택한 프로토타입 화면 크게 보기`, `View the selected prototype screen larger`],
    [`Unity 교실에서 학생 머리 위 말풍선으로 생성형 AI 응답이 표시되고 교사가 세 가지 대응 중 하나를 선택하는 화면`, `A Unity classroom screen showing a generative AI response in a speech bubble above a student while the teacher chooses one of three responses.`],
    [`생성형 학생과 직접 대화`, `Direct dialogue with a generative student`],
    [`학생 머리 위 말풍선, 실시간 관찰, 교사 대응 선택이 한 시야에 연결됩니다.`, `A speech bubble above the student, live observation, and teacher response choices connect in one view.`],
    [`프로토타입 증거 화면 선택`, `Select a prototype evidence screen`],
    [`책상을 원형으로 배치한 Unity 교실에서 학생의 발표 회피 상황에 대응하는 훈련 화면`, `A training screen for responding to presentation avoidance in a Unity classroom with desks arranged in a circle.`],
    [`원형 토론과 발표 상황`, `Circle discussion and presentation scenario`],
    [`원형 토론`, `Circle discussion`],
    [`발표 회피와 또래 맥락`, `Presentation avoidance and peer context`],
    [`발표 회피, 또래의 시선, 교사 개입을 별도의 두 번째 훈련 씬에서 다룹니다.`, `Presentation avoidance, peer attention, and teacher intervention are explored in a separate second training scene.`],
    [`한국 초등학교 Unity 교실에서 여러 학생이 상체를 세우고 교사 시점을 바라보는 디브리핑 장면`, `A debriefing scene in a Korean elementary Unity classroom where students sit upright and look toward the teacher's viewpoint.`],
    [`교사 시점과 아이컨택`, `Teacher viewpoint and eye contact`],
    [`아이컨택`, `Eye contact`],
    [`시선, 자세, 참여 신호`, `Gaze, posture, and participation cues`],
    [`학생별 시선과 자세를 분리해 교사의 위치와 대화 상태에 반응하도록 구성합니다.`, `Each student's gaze and posture respond to the teacher's position and the state of the conversation.`],
    [`Unity 한국 교실 책상 옆에 크기와 색이 다른 책가방과 물통이 걸려 있는 환경 디테일`, `An environmental detail from a Korean Unity classroom, with backpacks and water bottles of different sizes and colors hanging beside desks.`],
    [`한국 교실의 생활 디테일`, `Everyday details of a Korean classroom`],
    [`교실 디테일`, `Classroom details`],
    [`책가방과 생활 환경`, `Backpacks and everyday context`],
    [`책상 비율, 책가방, 물통, 수납장, 게시물처럼 교사의 판단에 맥락을 주는 생활 환경을 개별 에셋으로 재현합니다.`, `Everyday context that informs teacher judgment, including desk proportions, backpacks, water bottles, storage, and classroom displays, is recreated as individual assets.`],
    [`프로토타입 증거 화면 전체`, `All prototype evidence screens`],
    [`생성형 학생과 직접 대화하는 Unity 화면`, `A Unity screen for direct dialogue with a generative student`],
    [`원형 토론과 발표 상황을 다루는 Unity 화면`, `A Unity screen for circle discussion and presentation scenarios`],
    [`학생들이 교사 시점을 바라보는 Unity 화면`, `A Unity screen where students look toward the teacher's viewpoint`],
    [`책상 옆 책가방과 물통을 보여주는 Unity 화면`, `A Unity screen showing backpacks and water bottles beside desks`],
    [`한국 교실 생활 디테일`, `Everyday details of a Korean classroom`],
    [`Research tracks / 연구 트랙`, `Research tracks`],
    [`설계, 상호작용, 분석,`, `Design, interaction, and analysis,`],
    [`확장을 잇는 네 개의 축`, `four linked tracks for expansion`],
    [`제안서의 연구문제와 현재 프로토타입을 네 개의 연결된 트랙으로 정리했습니다. 각 트랙은 독립된 기능 목록이 아니라 다음 연차의 검증으로 이어지는 연구 단위입니다.`, `The proposal's research questions and current prototype are organized into four connected tracks. Each track is a research unit that leads to the next year's validation, not an isolated feature list.`],
    [`클래스룸 오케스트레이션과 ECD`, `Classroom orchestration and ECD`],
    [`정서·행동 신호의 인지, 우선순위 판단, 개입 시점과 전략을 수행 과제와 관찰 가능한 증거로 연결합니다. 안전한 선택만 연습하는 것이 아니라 판단의 이유와 후속 조치를 함께 다룹니다.`, `Connect recognition of emotional and behavioral signals, priority judgments, and intervention timing and strategies to performance tasks and observable evidence. The training addresses why a decision was made and what follows, not only safe choices.`],
    [`방법 축`, `Method spine`],
    [`설계기반연구(DBR) · Evidence-Centered Design · 전문가 면담 · 시나리오 및 스토리보드`, `Design-based research (DBR) · Evidence-Centered Design · expert interviews · scenarios and storyboards`],
    [`생성형 AI 학생 에이전트`, `Generative AI student agent`],
    [`교사는 정해진 대사만 고르는 대신 학생과 직접 대화할 수 있습니다. 응답 내용은 정서가와 연결되고, 시선, 자연스러운 제스처, 얼굴 Action Unit이 장면 안에서 연속적으로 전이됩니다.`, `Teachers can talk directly with students instead of choosing only scripted lines. Response content connects to affect, while gaze, natural gestures, and facial Action Units transition continuously within the scene.`],
    [`상호작용 계층`, `Interaction layer`],
    [`OpenRouter LLM · 로컬 fallback · 음성 입출력 · 정서가(VAD) · 얼굴 AU · 제스처 마이크로 제어`, `OpenRouter LLM · local fallback · voice input/output · valence-arousal-dominance (VAD) · facial AU · gesture micro-controls`],
    [`멀티모달 학습분석과 한·미 검증`, `Multimodal learning analytics and Korea–U.S. validation`],
    [`교사의 발화 내용과 어조, 반응 속도, 선택 경로, 시선과 장면 맥락을 함께 분석하는 파이프라인을 구축하고, 한국과 미국의 현직·예비교사 연구로 교육적 효과와 사용성을 검증할 계획입니다.`, `We will build a pipeline that analyzes teacher speech and tone, response speed, choice paths, gaze, and scene context together, then examine educational effects and usability with practicing and preservice teachers in Korea and the United States.`],
    [`예정 근거`, `Planned evidence`],
    [`사전·사후 비교 · 사용성 · 의사결정 로그 · 멀티모달 패턴 · 국가 간 맥락 비교`, `Pre/post comparison · usability · decision logs · multimodal patterns · cross-national context comparison`],
    [`학생 사회정서학습(SEL) 확장`, `Student social and emotional learning (SEL) expansion`],
    [`3차년도에는 교사용 훈련에서 축적한 설계 원리를 학생의 자기인식, 자기관리, 사회적 인식, 관계기술, 책임 있는 의사결정 연습으로 확장합니다. 초등학생이 안전하게 선택하고 성찰하는 게이미피케이션 구조를 탐색합니다.`, `In Year 3, design principles accumulated through teacher training will expand into student practice in self-awareness, self-management, social awareness, relationship skills, and responsible decision-making. We will explore a gamified structure in which elementary students choose and reflect safely.`],
    [`3차년도 초점`, `Year 03 focus`],
    [`CASEL 5 역량 · 또래 갈등 · 윤리적 딜레마 · 감정 어휘 · 의사결정 패턴`, `CASEL 5 competencies · peer conflict · ethical dilemmas · emotion vocabulary · decision patterns`],
    [`Three-year roadmap / 연구계획`, `Three-year roadmap / Research plan`],
    [`작동하는 프로토타입에서`, `From a working prototype`],
    [`비교 검증과 SEL 확장까지`, `to comparative validation and SEL expansion`],
    [`아래 일정과 학술 산출물은 제안서에 따른 계획입니다. 현재 구현 완료를 의미하지 않으며, 연구 승인과 현장 여건에 따라 조정될 수 있습니다.`, `The schedule and scholarly outputs below are proposal plans. They do not indicate completed implementation and may change with research approval and field conditions.`],
    [`설계 메커니즘과 프로토타입`, `Design mechanisms and prototype`],
    [`문헌·사례 분석, 전문가 면담, ECD 프레임워크, 시나리오와 스토리보드를 만들고 생성형 AI 통합 시뮬레이션의 사용성과 의사결정 지원을 점검합니다.`, `We will analyze literature and cases, interview experts, develop an ECD framework, and build scenarios and storyboards to examine the usability and decision support of the generative AI-integrated simulation.`],
    [`계획 산출물`, `Planned outputs`],
    [`설계 원리 · 사용성 근거 · AERA 2027 발표 추진`, `Design principles · usability evidence · AERA 2027 presentation target`],
    [`한·미 비교와 학습분석`, `Korea–U.S. comparison and learning analytics`],
    [`정서위기 상황 시나리오를 확장하고 현직·예비교사의 사전·사후 변화를 비교합니다. 상호작용 로그와 멀티모달 데이터를 분석해 의사결정 패턴과 학습 경로를 탐색합니다.`, `We will expand emotional-crisis scenarios and compare pre/post change among practicing and preservice teachers. Interaction logs and multimodal data will reveal decision patterns and learning paths.`],
    [`효과성 근거 · 분석 파이프라인 · 국제 저널 투고 추진`, `Effectiveness evidence · analytics pipeline · international journal submission target`],
    [`학생 SEL과 통합 모형`, `Student SEL and integrated model`],
    [`CASEL 5 역량을 중심으로 학생용 시나리오와 게이미피케이션을 개발하고, 사회정서역량 변화와 로그 기반 행동 패턴을 함께 살펴 교사·학생 통합 지원 모형을 제안합니다.`, `Centered on the CASEL 5 competencies, we will develop student scenarios and gamification, examine changes in social-emotional competence alongside log-based behavior patterns, and propose an integrated teacher-student support model.`],
    [`학생 SEL 시뮬레이션 · 현장 확산 모형 · ETR&D 투고 추진`, `Student SEL simulation · field dissemination model · ETR&D submission target`],
    [`Core research team / 연구팀`, `Core research team / Research team`],
    [`설계 이론, 현장 개발,`, `Design theory, field development,`],
    [`학습분석을 함께 책임진다`, `and learning analytics, together`],
    [`공개 제안서에 기재된 핵심 연구진과 역할입니다. 연락처와 비공개 운영 정보는 공개하지 않습니다.`, `These are the core researchers and roles listed in the public proposal. Contact details and private operating information are not disclosed.`],
    [`임`, `CL`],
    [`임철일`, `Cheolil Lim`],
    [`연구책임자`, `Principal investigator`],
    [`서울대학교 교육학과 교수`, `Professor, Department of Education, Seoul National University`],
    [`연구 설계와 총괄, 가상현실 시뮬레이션 설계원리 개발, 이론적 엄밀성과 연구 성과의 질 관리`, `Research design and leadership, development of virtual-reality simulation principles, and quality control for theoretical rigor and research outputs`],
    [`문`, `JM`],
    [`문제웅`, `Jewoong Moon`],
    [`해외공동연구원`, `International co-investigator`],
    [`Instructional Technology 조교수`, `Assistant Professor of Instructional Technology`],
    [`생성형 AI 통합 웹·XR 시뮬레이션 개발, 국외 연구 협력, 상호작용 로그와 학습분석 파이프라인`, `Development of generative AI-integrated web and XR simulations, international research collaboration, and interaction-log and learning-analytics pipelines`],
    [`홍`, `SH`],
    [`홍수민`, `Sumin Hong`],
    [`박사급연구원 · 실무 총괄`, `PhD-level researcher · operations lead`],
    [`서울대학교 학습과학연구소 연구원`, `Researcher, Learning Sciences Research Institute, Seoul National University`],
    [`시뮬레이션 설계·개발·평가 전 과정, 국내외 데이터 수집 및 분석, 연구진 협업과 단계별 산출물 관리`, `End-to-end simulation design, development, and evaluation; domestic and international data collection and analysis; research-team coordination and milestone deliverables`],
    [`Research boundaries / 연구 경계`, `Research boundaries`],
    [`안전한 연습은`, `Safe practice begins`],
    [`명확한 경계에서 시작한다`, `with clear boundaries`],
    [`교육 훈련 도구`, `Educational training tool`],
    [`교사의 관찰과 대응 연습을 지원하며, 학생을 진단하거나 임상 치료를 대체하지 않습니다.`, `The project supports teacher observation and response practice; it does not diagnose students or replace clinical care.`],
    [`계획과 결과의 구분`, `Plans are not results`],
    [`3개년 일정과 논문·학술대회는 추진 계획으로 표시하고, 현재 검증된 프로토타입 지표와 분리합니다.`, `The three-year schedule and papers and conferences are marked as plans and kept separate from currently verified prototype metrics.`],
    [`개인정보와 연구 승인`, `Privacy and research approval`],
    [`향후 음성, 시선, 반응 시간 등 연구 데이터는 기관 연구윤리 심의와 데이터 최소화 원칙 아래 다룰 계획입니다.`, `Future research data, including voice, gaze, and response time, will be handled under institutional ethics review and data-minimization principles.`],
    [`인간의 감독`, `Human oversight`],
    [`생성형 AI 응답은 훈련 맥락과 안전 규칙 안에서 사용하며, 실패 시 로컬 응답으로 전환하고 교사와 연구자의 판단을 우선합니다.`, `Generative AI responses are used within the training context and safety rules; on failure, the system switches to local responses and prioritizes teacher and researcher judgment.`],
    [`2026 공동연구지원사업(해외유형) 제안서 기반 3개년 연구계획과 Unity 프로토타입 개발 스냅샷.`, `A three-year research plan based on the 2026 collaborative research support proposal (international track), with a Unity prototype development snapshot.`],
    [`Educatian으로 돌아가기`, `Back to Educatian`],
    [`페이지 위로`, `Back to top`],
    [`연구계획 기간 2026.06.01–2029.05.31 · Prototype snapshot 2026.07.17`, `Research plan period 2026.06.01–2029.05.31 · Prototype snapshot 2026.07.17`],
    [`© 2026 Research Team. Public project overview.`, `© 2026 Research Team. Public project overview.`],
    [`프로토타입 화면 크게 보기`, `View prototype screen larger`],
    [`닫기`, `Close`],
    [`생성형 학생과 직접 대화하는 Unity 프로토타입 화면`, `A Unity prototype screen for direct dialogue with a generative student`]
  ];

  const languageLookup = new Map();
  languagePairs.forEach(([ko, en]) => {
    if (!languageLookup.has(ko)) languageLookup.set(ko, { ko, en });
    if (!languageLookup.has(en)) languageLookup.set(en, { ko, en });
  });

  const normalizeLanguageValue = (value) => value.trim().replace(/\s+/gu, " ");
  const translateValue = (value, language) => {
    const normalized = normalizeLanguageValue(value);
    const pair = languageLookup.get(normalized);
    if (!pair) return null;
    const translated = pair[language];
    const leading = value.match(/^\s*/u)?.[0] ?? "";
    const trailing = value.match(/\s*$/u)?.[0] ?? "";
    return `${leading}${translated}${trailing}`;
  };

  const translateTextNodes = (language) => {
    const textWalker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const textNodes = [];
    let currentNode = textWalker.nextNode();
    while (currentNode) {
      textNodes.push(currentNode);
      currentNode = textWalker.nextNode();
    }
    textNodes.forEach((textNode) => {
      if (textNode.parentElement?.closest("script, style, .hero__english, .identity-card__name-en")) return;
      const translated = translateValue(textNode.nodeValue ?? "", language);
      if (translated !== null) textNode.nodeValue = translated;
    });
  };

  const translateAttributes = (language) => {
    const selectors = ["alt", "aria-label", "data-alt", "data-title", "data-description", "title", "content"]
      .map((attribute) => `[${attribute}]`)
      .join(",");
    document.querySelectorAll(selectors).forEach((element) => {
      ["alt", "aria-label", "data-alt", "data-title", "data-description", "title", "content"].forEach((attribute) => {
        if (!element.hasAttribute(attribute)) return;
        const value = element.getAttribute(attribute) ?? "";
        const translated = translateValue(value, language);
        if (translated !== null) element.setAttribute(attribute, translated);
      });
    });
  };

  const languageToggle = document.querySelector("[data-language-toggle]");
  const languageOptions = Array.from(languageToggle?.querySelectorAll("[data-lang-option]") ?? []);
  const languageStorageKeys = ["teacher-response-simulation-language", "teacher-response-language"];
  const validLanguages = new Set(["ko", "en"]);
  let currentLanguage = "ko";

  const readLanguageFromUrl = () => {
    const value = new URLSearchParams(window.location.search).get("lang")?.toLowerCase();
    return validLanguages.has(value) ? value : null;
  };
  const readStoredLanguage = () => {
    for (const key of languageStorageKeys) {
      try {
        const value = window.localStorage.getItem(key)?.toLowerCase();
        if (validLanguages.has(value)) return value;
      } catch {
        return null;
      }
    }
    return null;
  };
  const persistLanguage = (language) => {
    languageStorageKeys.forEach((key) => {
      try {
        window.localStorage.setItem(key, language);
      } catch {
      }
    });
  };
  const updateLanguageUrl = (language) => {
    try {
      const url = new URL(window.location.href);
      url.searchParams.set("lang", language);
      window.history.replaceState({}, "", `${url.pathname}${url.search}${url.hash}`);
    } catch {
    }
  };

  const updateLanguageControl = (language) => {
    if (!languageToggle) return;
    languageToggle.setAttribute("aria-pressed", String(language === "en"));
    languageToggle.setAttribute("aria-label", language === "en" ? "Switch to Korean" : "Switch to English");
    languageToggle.dataset.language = language;
    languageOptions.forEach((option) => {
      const selected = option.dataset.langOption === language;
      option.classList.toggle("is-selected", selected);
      option.dataset.active = String(selected);
      option.setAttribute("aria-current", selected ? "true" : "false");
    });
  };

  const applyLanguage = (language, { persist = true, updateUrl = false } = {}) => {
    if (!validLanguages.has(language)) return;
    currentLanguage = language;
    root.lang = language;
    root.dataset.language = language;
    document.title = translateValue(document.title, language) ?? document.title;
    translateTextNodes(language);
    translateAttributes(language);
    const locale = document.querySelector('meta[property="og:locale"]');
    locale?.setAttribute("content", language === "en" ? "en_US" : "ko_KR");
    updateLanguageControl(language);
    if (persist) persistLanguage(language);
    if (updateUrl) updateLanguageUrl(language);

    const selectedTab = galleryTabs.find((tab) => tab.classList.contains("is-selected"));
    if (selectedTab) selectEvidence(selectedTab);
  };

  languageToggle?.addEventListener("click", (event) => {
    const target = event.target instanceof Element ? event.target.closest("[data-lang-option]") : null;
    const requestedLanguage = target?.getAttribute("data-lang-option");
    const nextLanguage = validLanguages.has(requestedLanguage) ? requestedLanguage : currentLanguage === "ko" ? "en" : "ko";
    applyLanguage(nextLanguage, { updateUrl: true });
  });
  window.addEventListener("popstate", () => {
    const language = readLanguageFromUrl();
    if (language) applyLanguage(language);
  });

  applyLanguage(readLanguageFromUrl() ?? readStoredLanguage() ?? "ko", { updateUrl: false });
})();
