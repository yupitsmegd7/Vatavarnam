import Avatar from './Avatar';

export default function AvatarGroup({ avatars = [], size = 40 }) {
  const groupStyle = {
    display: 'flex',
  };

  const itemStyle = (index) => ({
    marginLeft: index === 0 ? 0 : -12,
    position: 'relative',
    zIndex: avatars.length - index,
  });

  return (
    <div className="avatar-group" style={groupStyle}>
      {avatars.map((avatar, index) => (
        <div key={avatar.id ?? index} style={itemStyle(index)}>
          <Avatar src={avatar.src} alt={avatar.alt} size={size} />
        </div>
      ))}
    </div>
  );
}