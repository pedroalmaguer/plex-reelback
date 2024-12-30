class MatrixRain {
    constructor() {
        this.canvas = document.createElement('canvas');
        this.canvas.classList.add('matrix-rain');
        document.body.appendChild(this.canvas);
        this.ctx = this.canvas.getContext('2d');
        
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
        
        this.characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$@#%&*';
        this.fontSize = 14;
        this.columns = 0;
        this.drops = [];
        
        this.initMatrix();
        this.animate();
        
        // Scroll handling
        this.lastScroll = window.scrollY;
        window.addEventListener('scroll', () => this.handleScroll());
    }
    
    resizeCanvas() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.initMatrix();
    }
    
    initMatrix() {
        this.columns = Math.floor(this.canvas.width / this.fontSize);
        this.drops = [];
        for (let i = 0; i < this.columns; i++) {
            this.drops[i] = 1;
        }
    }
    
    handleScroll() {
        const currentScroll = window.scrollY;
        const scrollSpeed = Math.abs(currentScroll - this.lastScroll);
        this.lastScroll = currentScroll;
        
        // Adjust rain speed based on scroll speed
        this.rainSpeed = Math.min(scrollSpeed / 10, 25);
        
        document.body.classList.add('matrix-scroll');
        setTimeout(() => {
            document.body.classList.remove('matrix-scroll');
        }, 500);
    }
    
    animate() {
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.ctx.fillStyle = '#33ff33';
        this.ctx.font = `${this.fontSize}px monospace`;
        
        for (let i = 0; i < this.drops.length; i++) {
            const text = this.characters[Math.floor(Math.random() * this.characters.length)];
            this.ctx.fillText(text, i * this.fontSize, this.drops[i] * this.fontSize);
            
            if (this.drops[i] * this.fontSize > this.canvas.height && Math.random() > 0.975) {
                this.drops[i] = 0;
            }
            this.drops[i]++;
        }
        requestAnimationFrame(() => this.animate());
    }
} 