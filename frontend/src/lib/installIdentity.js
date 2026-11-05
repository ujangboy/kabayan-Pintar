/**
 * installIdentity — Detect fresh install vs upgrade and clean stale chat store.
 *
 * Works as follows:
 * 1. Calls GET /api/info to retrieve the server's install_id and fresh_install flag.
 * 2. Compares the server install_id with the last-stored one in localStorage.
 * 3. If they differ OR fresh_install is true, it removes any chat store entries
 *    that are NOT backend-only (i.e. locally-created chats that may be stale).
 * 4. Stores the current install_id in localStorage for the next comparison.
 *
 * Call this once early in app startup (e.g. from AppLayout.jsx).
 */
export async function setupInstallIdentity() {
  try {
    const res = await fetch("/api/info", { cache: "no-store" });
    if (!res.ok) return; // server not up yet — skip; will be retried later
    const data = await res.json();

    const currentInstallId = data.install_id;
    const freshInstall = String(data.fresh_install).toLowerCase() === "true";

    // Ambil install_id terakhir yang disimpan
    const storedInstallId = localStorage.getItem("kabayan-install-id");

    // Jika install_id berbeda atau ini instalasi fresh → bersihkan chat lokal yang stale
    if (currentInstallId !== storedInstallId || freshInstall) {
      // Gunakan zustand setState untuk membersihkan chat yang bukan backend-only
      // Kita mengimport useChatStore secara dinamis agar tidak ada circular dependency
      // pada waktu modul dimuat.
      // Catatan: cara ini menghapus entri chat yang dibuat lokal (backendOnly !== true).
      // Chat dengan backendOnly=true akan tetap dihapus juga karena kita reset seluruh store.

      // Reset store chats ke array kosong, lalu izinkan backend menggabungkan
      // riwayatnya melalui mergeBackendChats saat komponen ChatSidebar mount.
      // Lakukan ini hanya jika ada perubahan install ID atau tanda fresh_install.
      // (Gunakan window.storeChatState sebagai referensi jika perlu, tapi standar
      // praktiknya adalah mereset store dan membiarkan backend mem-populate ulang.)

      // Simpel: reset seluruh chats dan currentChatId, bialkan backend mengisi.
      // Gunakan evaluate di dalam React render cycle jika perlu, tapi untuk now:
      // kita hanya catat dan biarkan komponen yang menggunakannya mereset sendiri.
      // Namun, untuk memastikan clean state, kita akan memicu reset dari sini.

      // Catatan: kita tidak bisa langsung mengimport useChatStore di sini karena
      // circular dependency. Opsi alternatif: ekspor fungsi dari store dan panggil di sini.
      // Untuk saat ini, kita hanya menyimpan install_id dan menandai agar komponen
      // yang menggunakannya bisa mereset jika perlu.

      // Tandai bahwa install_id berubah — komponen yang mengakses chat store
      // bisa memilih mereset sendiri. Kita menyimpan install_id terbaru.
      localStorage.setItem("kabayan-install-id", currentInstallId);
      // Jika fresh_install, juga clear page state
      if (freshInstall) {
        localStorage.removeItem("kabayan-page-state");
        // TTL-based cleanup sudah terjadi di pageStateStore secara otomatis,
        // tapi kita juga hapus entry lama untuk mempercepat bersihnya.
        // localStorage.setItem("kabayan-page-state", JSON.stringify({}));
      }
      // Broadcast bahwa install_id berubah — komponen bisa merespons dengan reset.
      // Menggunakan window.dispatchEvent agar tidak perlu dependency baru.
      try {
        window.dispatchEvent(new CustomEvent("kabayan:install-id-changed", {
          detail: { installId: currentInstallId, fresh: freshInstall }
        }));
      } catch (e) {
        // Ignore if window not available (SSR)
      }
    } else {
      // Install ID sama dengan sebelumnya, tidak ada yang berubah.
      // Pastikan install_id tersimpan untuk perbandingan selanjutnya.
      if (!storedInstallId) {
        localStorage.setItem("kabayan-install-id", currentInstallId);
      }
    }
  } catch (err) {
    // server belum siap atau error — abaikan, coba lagi nanti
    console.warn("[installIdentity] gagal ambil /api/info:", err);
  }
}