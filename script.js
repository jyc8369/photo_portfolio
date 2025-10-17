// 전역 변수들
let allPhotoData = []; // 모든 사진 데이터 저장
let currentFilter = 'all'; // 현재 필터 상태
let imageObserver; // IntersectionObserver 인스턴스

// 사진 데이터 로드 (메타데이터만)
async function loadPhotoMetadata() {
    try {
        const response = await fetch('photos.json');
        allPhotoData = await response.json();
        console.log(`${allPhotoData.length}개의 사진 메타데이터 로드 완료`);

        // 초기 갤러리 생성 (플레이스홀더만)
        createGalleryPlaceholders();

        // 이벤트 바인딩
        bindEvents();

        // 초기 필터링 적용
        filterPhotos('all');

    } catch (error) {
        console.error('사진 메타데이터를 로드하는 중 오류 발생:', error);
    }
}

// 갤러리에 플레이스홀더 생성
function createGalleryPlaceholders() {
    const gallery = document.querySelector('.gallery');
    gallery.innerHTML = ''; // 기존 내용 초기화

    allPhotoData.forEach((data, index) => {
        const photoDiv = document.createElement('div');
        photoDiv.className = 'photo';
        photoDiv.dataset.index = index;
        const categories = Array.isArray(data.category) ? data.category : [data.category];
        photoDiv.dataset.category = categories.join(',');
        photoDiv.dataset.alt2 = data.alt2 || '';

        // 제목 추가
        const title = document.createElement('h3');
        title.textContent = data.title || data.alt;
        photoDiv.appendChild(title);

        // 이미지 플레이스홀더 (실제 이미지는 로드하지 않음)
        const img = document.createElement('img');
        img.className = 'photo-placeholder';
        img.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkxvYWRpbmcuLi48L3RleHQ+PC9zdmc+';
        img.alt = 'Loading...';
        img.dataset.src = data.src; // 실제 이미지 경로 저장
        img.dataset.alt = data.alt;

        photoDiv.appendChild(img);
        gallery.appendChild(photoDiv);
    });
}

// 실제 이미지 로드 함수
function loadActualImage(imgElement) {
    if (imgElement.classList.contains('loaded')) return; // 이미 로드된 경우

    const actualSrc = imgElement.dataset.src;
    const actualAlt = imgElement.dataset.alt;

    // 실제 이미지 로드
    const actualImg = new Image();
    actualImg.onload = function() {
        imgElement.src = actualSrc;
        imgElement.alt = actualAlt;
        imgElement.classList.add('loaded');
        imgElement.classList.remove('photo-placeholder');
    };
    actualImg.src = actualSrc;
}

// IntersectionObserver 설정
function setupImageObserver() {
    if (imageObserver) {
        imageObserver.disconnect(); // 기존 observer 해제
    }

    imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                loadActualImage(img);
                observer.unobserve(img); // 한 번 로드되면 관찰 중지
            }
        });
    }, {
        rootMargin: '50px' // 화면에 50px 전에 로드 시작
    });

    // 현재 표시된 사진들의 이미지만 관찰
    const visiblePhotos = document.querySelectorAll('.photo[style*="display: block"], .photo:not([style*="display: none"])');
    visiblePhotos.forEach(photo => {
        const img = photo.querySelector('img.photo-placeholder');
        if (img && !img.classList.contains('loaded')) {
            imageObserver.observe(img);
        }
    });
}

// 필터링 함수 (개선됨)
function filterPhotos(category) {
    currentFilter = category;
    const photos = document.querySelectorAll('.photo');

    photos.forEach(photo => {
        const photoCategory = photo.dataset.category.split(',');
        if (category === 'all' || photoCategory.includes(category)) {
            photo.style.display = 'block';
        } else {
            photo.style.display = 'none';
        }
    });

    // 필터링 후 이미지 관찰자 재설정
    setTimeout(setupImageObserver, 100);
}

// 이벤트 바인딩
function bindEvents() {
    // 필터 버튼 이벤트
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            filterButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            filterPhotos(button.dataset.category);
        });
    });

    // 사진 클릭 이벤트 (동적 바인딩)
    document.addEventListener('click', (e) => {
        if (e.target.closest('.photo')) {
            const photoDiv = e.target.closest('.photo');
            openLightbox(photoDiv);
        }
    });
}

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

// 페이지 로드 시 사진 메타데이터 로드
document.addEventListener('DOMContentLoaded', loadPhotoMetadata);

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