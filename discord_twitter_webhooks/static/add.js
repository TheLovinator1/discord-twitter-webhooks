document.addEventListener('DOMContentLoaded', () => {
    const checkbox_send_embed = document.querySelector('#send_as_embed');
    const div_embed_settings = document.querySelector('#embed_settings');
    const checkbox_send_text = document.querySelector('#send_as_text');
    const div_text_settings = document.querySelector('#text_settings');
    const checkbox_send_link = document.querySelector('#send_as_link');
    const div_link_settings = document.querySelector('#link_settings');

    // Check if checkbox for embed is checked on page load
    if (checkbox_send_embed.checked) {
        div_embed_settings.style.display = 'block';
        // div_text_settings.style.display = 'none';
        div_link_settings.style.display = 'none';
    } else if (checkbox_send_link.checked) {
        div_link_settings.style.display = 'block';
        div_embed_settings.style.display = 'none';
        // div_text_settings.style.display = 'none';
    } else {
        div_embed_settings.style.display = 'none';
        // div_text_settings.style.display = 'none';
        div_link_settings.style.display = 'none';
    }


    // Display settings for embed and hide settings for text and link
    checkbox_send_embed.addEventListener('change', () => {
        if (checkbox_send_embed.checked) {
            console.log('Checkbox for embed is checked');
            div_embed_settings.style.display = 'block';
            // div_text_settings.style.display = 'none';
            div_link_settings.style.display = 'none';
        }
    });

    // Display settings for text and hide settings for embed and link
    checkbox_send_text.addEventListener('change', () => {
        if (checkbox_send_text.checked) {
            div_embed_settings.style.display = 'none';
            div_link_settings.style.display = 'none';
        }
    });

    // Display settings for link and hide settings for embed and text
    checkbox_send_link.addEventListener('change', () => {
        if (checkbox_send_link.checked) {
            div_link_settings.style.display = 'block';
            div_embed_settings.style.display = 'none';
            // div_text_settings.style.display = 'block';
        }
    });
});
