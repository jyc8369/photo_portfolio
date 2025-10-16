// 사진 데이터 로드 및 갤러리 생성
async function loadPhotos() {
    try {
        const response = await fetch('photos.json');
        const photoData = await response.json();
        const gallery = document.querySelector('.gallery');

        photoData.forEach(data => {
            const photoDiv = document.createElement('div');
            photoDiv.className = 'photo';
            const categories = Array.isArray(data.category) ? data.category : [data.category];
            photoDiv.dataset.category = categories.join(','); // 여러 카테고리 지원
            photoDiv.dataset.alt2 = data.alt2 || '';  // 설명2 추가

            const title = document.createElement('h3');
            title.textContent = data.title || data.alt;
            photoDiv.appendChild(title);

            const img = document.createElement('img');
            img.src = data.src;
            img.alt = data.alt;
            img.loading = 'lazy';

            photoDiv.appendChild(img);
            gallery.appendChild(photoDiv);
        });

        // 사진 로드 후 이벤트 바인딩
        bindPhotoEvents();
    } catch (error) {
        console.error('사진 데이터를 로드하는 중 오류 발생:', error);
    }
}

// 사진 이벤트 바인딩
function bindPhotoEvents() {
    photos = document.querySelectorAll('.photo');
    photos.forEach((photo) => {
        photo.addEventListener('click', (e) => {
            openLightbox(e.currentTarget);
        });
    });
}

// 필터 버튼
const filterButtons = document.querySelectorAll('.filter-btn');
let photos = document.querySelectorAll('.photo'); // 동적으로 업데이트

// 필터링 함수
function filterPhotos(category) {
    photos = document.querySelectorAll('.photo'); // 동적으로 가져오기
    photos.forEach(photo => {
        const photoCategory = photo.dataset.category.split(','); // 여러 카테고리 지원
        if (category === 'all' || photoCategory.includes(category)) {
            photo.style.display = 'block';
        } else {
            photo.style.display = 'none';
        }
    });
}

// 필터 버튼 이벤트
filterButtons.forEach(button => {
    button.addEventListener('click', () => {
        filterButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        filterPhotos(button.dataset.category);
    });
});

// 라이트박스
const lightbox = document.getElementById('lightbox');
const lightboxImg = document.getElementById('lightbox-img');
const closeBtn = document.querySelector('.close');
const prevBtn = document.querySelector('.prev');
const nextBtn = document.querySelector('.next');

let currentIndex = 0;
let visiblePhotos = [];

// 라이트박스 열기
function openLightbox(clickedPhoto) {
    visiblePhotos = Array.from(photos).filter(photo => photo.style.display !== 'none');
    currentIndex = visiblePhotos.indexOf(clickedPhoto);
    if (currentIndex === -1) return; // 클릭된 사진이 필터링되지 않은 경우
    lightboxImg.src = visiblePhotos[currentIndex].querySelector('img').src;

    // 사진 컨테이너 생성
    const imageContainer = document.createElement('div');
    imageContainer.className = 'image-container';
    imageContainer.style.position = 'relative';
    imageContainer.style.display = 'flex';
    imageContainer.style.alignItems = 'center';

    // 사진 부분
    const imageWrapper = document.createElement('div');
    imageWrapper.style.flex = '1';
    imageWrapper.style.position = 'relative';

    imageWrapper.appendChild(lightboxImg);

    // 텍스트 부분
    const textWrapper = document.createElement('div');
    textWrapper.className = 'lightbox-text';
    textWrapper.style.flex = '0 0 20%'; // 20% 너비
    textWrapper.style.paddingLeft = '20px';

    const title = visiblePhotos[currentIndex].querySelector('h3').textContent;
    const alt = visiblePhotos[currentIndex].querySelector('img').alt;
    const alt2 = visiblePhotos[currentIndex].dataset.alt2 || '';  // 설명2 추가
    textWrapper.innerHTML = `<strong>${title}</strong><br><span style="font-size: 0.9em; opacity: 0.8;">${alt}</span><br><span style="font-size: 0.8em; opacity: 0.6;">${alt2}</span>`;

    imageContainer.appendChild(imageWrapper);
    imageContainer.appendChild(textWrapper);

    // 화살표 버튼을 lightbox-content 바깥에 배치
    const prevBtn = document.createElement('a');
    prevBtn.className = 'prev';
    prevBtn.innerHTML = '&#10094;';
    prevBtn.addEventListener('click', prevPhoto);

    const nextBtn = document.createElement('a');
    nextBtn.className = 'next';
    nextBtn.innerHTML = '&#10095;';
    nextBtn.addEventListener('click', nextPhoto);

    const lightbox = document.querySelector('.lightbox');
    lightbox.appendChild(prevBtn);
    lightbox.appendChild(nextBtn);

    const lightboxContent = document.querySelector('.lightbox-content');
    lightboxContent.appendChild(imageContainer);

    lightbox.classList.add('show'); // 애니메이션으로 열기
}

// 라이트박스 닫기
function closeLightbox() {
    lightbox.classList.remove('show'); // 애니메이션으로 닫기

    // 이미지 컨테이너 및 화살표 버튼 제거
    const imageContainer = document.querySelector('.image-container');
    if (imageContainer) {
        imageContainer.remove();
    }
    const prevBtn = document.querySelector('.prev');
    if (prevBtn) {
        prevBtn.remove();
    }
    const nextBtn = document.querySelector('.next');
    if (nextBtn) {
        nextBtn.remove();
    }
}

// 이전 사진
function prevPhoto() {
    currentIndex = (currentIndex > 0) ? currentIndex - 1 : visiblePhotos.length - 1;
    lightboxImg.src = visiblePhotos[currentIndex].querySelector('img').src;
}

// 다음 사진
function nextPhoto() {
    currentIndex = (currentIndex < visiblePhotos.length - 1) ? currentIndex + 1 : 0;
    lightboxImg.src = visiblePhotos[currentIndex].querySelector('img').src;
}

// 사진 클릭 이벤트 (동적으로 바인딩되므로 제거)
// photos.forEach((photo, index) => {
//     photo.addEventListener('click', () => {
//         openLightbox(index);
//     });
// });

// 페이지 로드 시 사진 로드
document.addEventListener('DOMContentLoaded', loadPhotos);

// 닫기 버튼
closeBtn.addEventListener('click', closeLightbox);

// 이전/다음 버튼
prevBtn.addEventListener('click', prevPhoto);
nextBtn.addEventListener('click', nextPhoto);

// ESC 키로 닫기
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeLightbox();
    } else if (e.key === 'ArrowLeft') {
        prevPhoto();
    } else if (e.key === 'ArrowRight') {
        nextPhoto();
    }
});

// 터치 이벤트 변수
let touchStartX = 0;
let touchEndX = 0;

// 터치 시작
function handleTouchStart(e) {
    touchStartX = e.changedTouches[0].screenX;
}

// 터치 끝
function handleTouchEnd(e) {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
}

// 스와이프 처리
function handleSwipe() {
    const swipeThreshold = 50; // 최소 스와이프 거리
    if (touchEndX < touchStartX - swipeThreshold) {
        nextPhoto(); // 왼쪽 스와이프: 다음
    }
    if (touchEndX > touchStartX + swipeThreshold) {
        prevPhoto(); // 오른쪽 스와이프: 이전
    }
}

// 라이트박스에 터치 이벤트 추가
lightbox.addEventListener('touchstart', handleTouchStart, false);
lightbox.addEventListener('touchend', handleTouchEnd, false);

// Lazy loading (이미 HTML에 loading="lazy" 추가됨, 추가로 IntersectionObserver 사용 가능)
const images = document.querySelectorAll('img[loading="lazy"]');

const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.src; // 이미 로딩 중이므로 추가 로직 필요 없음
            observer.unobserve(img);
        }
    });
});

images.forEach(img => imageObserver.observe(img));